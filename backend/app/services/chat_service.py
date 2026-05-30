from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import re
from ..models.chat_message import ChatMessage
from ..models.chat_checkout_state import ChatCheckoutState
from ..models.order import Order, OrderStatus
from ..models.order import PaymentMethod
from ..models.products import Product
from ..models.users import User
from ..models.cart import Cart
from ..models.cartItem import CartItem
from ..repositories.cart_repository import CartRepository
from ..repositories.order_repository import OrderRepository
from ..services.ollama_service import ollama_service, CART_TOOLS
from ..services.order_service import OrderService
from ..services.support_ticket_service import SupportTicketService


class ChatService:
    SUPPORT_STATUS_LABELS = {
        OrderStatus.created: "принят",
        OrderStatus.paid: "оплачен",
        OrderStatus.cooking: "готовится",
        OrderStatus.ready: "готов и ожидает отправки",
        OrderStatus.delivering: "в пути",
        OrderStatus.completed: "доставлен",
        OrderStatus.cancelled: "отменён",
    }
    PAYMENT_METHOD_LABELS = {
        PaymentMethod.cash_on_delivery.value: "Наличными при получении",
        PaymentMethod.credit_card.value: "Картой",
        PaymentMethod.sbp.value: "СБП",
    }
    STOPWORDS = {
        "и", "еще", "ещё", "плюс", "давай", "добавь", "добавляй", "мне",
        "пожалуйста", "хочу", "будет", "нужно", "надо", "закажи"
    }
    COMMENT_STARTERS = {
        "без", "с", "со", "на", "в", "отдельно", "побольше", "поменьше",
        "острый", "острое", "холодный", "теплый", "тёплый"
    }

    def __init__(self, db: Session):
        self.db = db

    def get_user_history(self, user_id: Optional[int] = None, session_id: Optional[str] = None, limit: int = 20) -> List[ChatMessage]:
        query = self.db.query(ChatMessage)
        
        if user_id and session_id:
            query = query.filter(
                ChatMessage.user_id == user_id,
                ChatMessage.session_id == session_id,
            )
        elif user_id:
            query = query.filter(ChatMessage.user_id == user_id)
        elif session_id:
            query = query.filter(ChatMessage.session_id == session_id)
        
        return (
            query.order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()[::-1]
        )

    def add_message(self, user_id: Optional[int], session_id: Optional[str], message: str, response: str) -> ChatMessage:
        chat_message = ChatMessage(
            user_id=user_id,
            session_id=session_id,
            message=message,
            response=response,
        )
        self.db.add(chat_message)
        self.db.commit()
        self.db.refresh(chat_message)
        return chat_message

    def _get_checkout_state(self, session_id: Optional[str]) -> Optional[ChatCheckoutState]:
        if not session_id:
            return None
        return self.db.query(ChatCheckoutState).filter(ChatCheckoutState.session_id == session_id).first()

    def _get_or_create_checkout_state(
        self,
        user_id: Optional[int],
        session_id: Optional[str],
    ) -> Optional[ChatCheckoutState]:
        if not session_id:
            return None

        state = self._get_checkout_state(session_id)
        if state:
            if user_id and not state.user_id:
                state.user_id = user_id
                self.db.commit()
                self.db.refresh(state)
            return state

        state = ChatCheckoutState(
            user_id=user_id,
            session_id=session_id,
            status="collecting",
        )
        self.db.add(state)
        self.db.commit()
        self.db.refresh(state)
        return state

    def _delete_checkout_state(self, state: Optional[ChatCheckoutState]) -> None:
        if not state:
            return
        self.db.delete(state)
        self.db.commit()

    def clear_history(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> int:
        query = self.db.query(ChatMessage)
        checkout_state = self._get_checkout_state(session_id) if session_id else None
        
        if user_id and session_id:
            query = query.filter(
                ChatMessage.user_id == user_id,
                ChatMessage.session_id == session_id,
            )
        elif user_id:
            query = query.filter(ChatMessage.user_id == user_id)
        elif session_id:
            query = query.filter(ChatMessage.session_id == session_id)
        
        count = query.count()
        query.delete()
        self.db.commit()
        if checkout_state:
            self._delete_checkout_state(checkout_state)
        return count

    def get_menu_context(self) -> str:
        products = self.db.query(Product).limit(50).all()
        
        menu_items = []
        for p in products:
            cat_name = p.category.name if p.category else "Другое"
            calories_total = None
            if p.calories and p.weight:
                calories_total = round((p.calories * p.weight) / 100)
            
            menu_items.append({
                "id": p.id,
                "name": p.name,
                "category": cat_name,
                "price": p.price,
                "description": p.description,
                "ingredients": p.ingredients or [],
                "calories": p.calories,  # на 100г
                "calories_total": calories_total,  # на всю порцию
                "weight": p.weight,
                "protein": p.protein,
                "fat": p.fat,
                "carbohydrates": p.carbohydrates
            })
        
        return json.dumps(menu_items, ensure_ascii=False)

    def _sanitize_assistant_response(self, text: str) -> str:
        cleaned = text or ""
        cleaned = re.sub(r"\s*\((?:id|ID)\s*[:=]?\s*\d+\)", "", cleaned)
        cleaned = re.sub(r"\b(?:id|ID)\s*[:=]?\s*\d+\b", "", cleaned)
        cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def _extract_calorie_budget(self, message: str) -> Optional[int]:
        normalized = self._normalize_text(message)
        match = re.search(r"\bдо\s*(\d+)\s*(?:ккал|калори(?:й|и|я))\b", normalized)
        if match:
            return int(match.group(1))
        return None

    def _is_combo_calorie_request(self, message: str) -> bool:
        normalized = self._normalize_text(message)
        return (
            self._extract_calorie_budget(message) is not None
            and "пицц" in normalized
            and "бургер" in normalized
        )

    def _build_calorie_combo_response(self, message: str, menu_list: List[Dict[str, Any]]) -> Optional[str]:
        if not self._is_combo_calorie_request(message):
            return None

        budget = self._extract_calorie_budget(message)
        if budget is None:
            return None

        pizzas = [
            item for item in menu_list
            if "пицц" in self._normalize_text(item.get("category", ""))
            and item.get("calories_total")
        ]
        burgers = [
            item for item in menu_list
            if "бургер" in self._normalize_text(item.get("category", ""))
            and item.get("calories_total")
        ]

        if not pizzas or not burgers:
            return "Не вижу в меню достаточно данных по калориям для пиццы и бургеров. Могу подсказать по отдельным позициям."

        valid_pairs = []
        all_pairs = []
        for pizza in pizzas:
            for burger in burgers:
                total = int(pizza["calories_total"]) + int(burger["calories_total"])
                pair = {
                    "pizza": pizza,
                    "burger": burger,
                    "total": total
                }
                all_pairs.append(pair)
                if total <= budget:
                    valid_pairs.append(pair)

        if valid_pairs:
            best_pair = max(valid_pairs, key=lambda pair: pair["total"])
            response_lines = [
                f"Под лимит {budget} ккал лучше всего подходит такая пара:",
                f"- {best_pair['pizza']['name']} — {best_pair['pizza']['calories_total']} ккал",
                f"- {best_pair['burger']['name']} — {best_pair['burger']['calories_total']} ккал",
                f"Итого: {best_pair['total']} ккал"
            ]

            alternatives = sorted(
                [pair for pair in valid_pairs if pair != best_pair],
                key=lambda pair: pair["total"],
                reverse=True
            )[:2]
            if alternatives:
                response_lines.append("")
                response_lines.append("Ещё варианты в лимите:")
                for pair in alternatives:
                    response_lines.append(
                        f"- {pair['pizza']['name']} + {pair['burger']['name']} — {pair['total']} ккал"
                    )

            response_lines.append("")
            response_lines.append("Если хочешь, сразу добавлю выбранную пару в корзину.")
            return "\n".join(response_lines)

        lightest_pair = min(all_pairs, key=lambda pair: pair["total"])
        return "\n".join([
            f"Пары пицца + бургер до {budget} ккал в текущем меню нет.",
            f"Самая лёгкая комбинация сейчас: {lightest_pair['pizza']['name']} — {lightest_pair['pizza']['calories_total']} ккал и {lightest_pair['burger']['name']} — {lightest_pair['burger']['calories_total']} ккал.",
            f"Итого: {lightest_pair['total']} ккал.",
            "Если хочешь, подберу вариант до лимита с пиццей и напитком или с бургером и напитком."
        ])

    def _normalize_text(self, text: str) -> str:
        text = (text or "").lower().replace("ё", "е")
        text = re.sub(r"[\"'`«»()!?.,:;]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _replace_number_words(self, text: str) -> str:
        normalized = self._normalize_text(text)
        replacements = {
            "1": "один",
            "2": "два",
            "3": "три",
            "4": "четыре",
            "5": "пять",
            "6": "шесть",
            "7": "семь",
            "8": "восемь",
            "9": "девять",
            "10": "десять",
        }
        for digit, word in replacements.items():
            normalized = re.sub(rf"\b{digit}\b", word, normalized)
        return normalized

    def _text_variants(self, text: str) -> List[str]:
        normalized = self._normalize_text(text)
        with_numbers_as_words = self._replace_number_words(text)
        variants = [normalized]
        if with_numbers_as_words != normalized:
            variants.append(with_numbers_as_words)
        return variants

    def _stem_token(self, token: str) -> str:
        token = self._normalize_text(token)
        endings = [
            "иями", "ями", "ами", "ого", "ему", "ому", "ыми", "ими", "его",
            "ая", "яя", "ую", "юю", "ой", "ей", "ый", "ий", "ые", "ие",
            "ым", "им", "ом", "ем", "ых", "их", "ам", "ям", "ах", "ях",
            "ов", "ев", "ом", "ем", "а", "я", "у", "ю", "ы", "и", "е", "о"
        ]
        for ending in endings:
            if len(token) > len(ending) + 2 and token.endswith(ending):
                return token[:-len(ending)]
        return token

    def _tokenize(self, text: str) -> List[str]:
        normalized = self._normalize_text(text)
        return [
            self._stem_token(token)
            for token in normalized.split()
            if token and token not in self.STOPWORDS
        ]

    def _extract_quantity(self, text: str, product_name: Optional[str] = None) -> int:
        normalized_text = self._normalize_text(text)
        normalized_product_name = self._normalize_text(product_name or "")
        product_variants = set(self._text_variants(product_name or ""))

        # Если сегмент по сути является названием товара "Четыре сыра" / "4 сыра",
        # не трактуем число как количество.
        if normalized_text in product_variants:
            return 1

        digit_match = re.search(r"\b(\d+)\b", text)
        if digit_match:
            return max(1, int(digit_match.group(1)))

        number_words = {
            "один": 1, "одна": 1, "одну": 1,
            "два": 2, "две": 2,
            "три": 3,
            "четыре": 4,
            "пять": 5,
            "шесть": 6,
            "семь": 7,
            "восемь": 8,
            "девять": 9,
            "десять": 10,
        }
        for word, value in number_words.items():
            if normalized_product_name.startswith(f"{word} "):
                continue
            if re.search(rf"\b{word}\b", normalized_text):
                return value
        return 1

    def _is_affirmative(self, message: str) -> bool:
        normalized = self._normalize_text(message)
        affirmative_patterns = [
            r"\bда\b", r"\bага\b", r"\bугу\b", r"\bок\b", r"\bокей\b", r"\bхорошо\b",
            r"\bдавай\b", r"\bдобавляй\b", r"\bдобавь\b", r"\bберу\b", r"\bхочу\b",
            r"\bпогнали\b", r"\bможно\b"
        ]
        return any(re.search(pattern, normalized) for pattern in affirmative_patterns)

    def _split_cart_request(self, message: str) -> List[str]:
        normalized = self._normalize_text(message)
        parts = re.split(r"\s*(?:,| и | плюс | а еще | ещё |;)\s*", normalized)
        return [part.strip() for part in parts if part.strip()]

    def _product_match_score(self, segment: str, product: Dict[str, Any]) -> int:
        segment_variants = self._text_variants(segment)
        name_variants = self._text_variants(product["name"])

        for segment_normalized in segment_variants:
            for name_normalized in name_variants:
                if name_normalized in segment_normalized:
                    return 100 + len(name_normalized)

        segment_tokens = set()
        for variant in segment_variants:
            segment_tokens.update(self._tokenize(variant))

        product_tokens = set()
        for variant in name_variants:
            product_tokens.update(
                token for token in self._tokenize(variant)
                if token not in {"пицц", "напит", "десерт"}
            )

        if not product_tokens:
            return 0

        overlap = len(segment_tokens & product_tokens)
        first_product_token = next(iter(self._tokenize(product["name"])), None)

        if overlap == len(product_tokens):
            return 80 + overlap * 10
        if first_product_token and first_product_token in segment_tokens:
            return 70
        if overlap > 0 and len(product_tokens) == 1:
            return 60 + overlap * 10
        if overlap >= 2:
            return 40 + overlap * 10
        return 0

    def _match_product_from_segment(self, segment: str, menu_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        best_product = None
        best_score = 0

        for product in menu_list:
            score = self._product_match_score(segment, product)
            if score > best_score:
                best_product = product
                best_score = score

        return best_product if best_score >= 60 else None

    def _extract_comment_from_segment(self, segment: str, product: Dict[str, Any]) -> Optional[str]:
        normalized_segment = self._normalize_text(segment)
        product_variants = sorted(
            set(self._text_variants(product["name"])),
            key=len,
            reverse=True
        )

        cleaned = normalized_segment
        matched_full_variant = False
        for variant in product_variants:
            if variant and variant in cleaned:
                cleaned = re.sub(rf"\b{re.escape(variant)}\b", " ", cleaned, count=1)
                matched_full_variant = True
                break

        if not matched_full_variant:
            product_tokens = set(self._tokenize(product["name"]))
            remaining_tokens = []
            removed_tokens = set()
            for token in cleaned.split():
                stem = self._stem_token(token)
                if stem in product_tokens and stem not in removed_tokens:
                    removed_tokens.add(stem)
                    continue
                remaining_tokens.append(token)
            cleaned = " ".join(remaining_tokens)

        cleaned = re.sub(r"\b\d+\b", " ", cleaned)
        cleaned = re.sub(
            r"\b(один|одна|одну|два|две|три|четыре|пять|шесть|семь|восемь|девять|десять)\b",
            " ",
            cleaned
        )

        tokens = [token for token in cleaned.split() if token]
        while tokens and tokens[0] in self.STOPWORDS:
            tokens.pop(0)

        if not tokens:
            return None

        if tokens[0] not in self.COMMENT_STARTERS and len(tokens) <= 2:
            return None

        comment = " ".join(tokens).strip()
        return comment or None

    def _extract_items_from_message(self, message: str, menu_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        items = []

        for segment in self._split_cart_request(message):
            product = self._match_product_from_segment(segment, menu_list)
            if not product:
                continue

            items.append({
                "product_id": product["id"],
                "quantity": self._extract_quantity(segment, product["name"]),
                "comment": self._extract_comment_from_segment(segment, product)
            })

        return items

    def _extract_suggested_item_from_context(
        self,
        message: str,
        context: List[dict],
        menu_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if not self._is_affirmative(message) or not context:
            return []

        last_response = context[-1]["response"]
        quoted_products = re.findall(r"«([^»]+)»", last_response)
        if not quoted_products:
            return []

        items = []
        for product_name in quoted_products:
            product = self._match_product_from_segment(product_name, menu_list)
            if product:
                items.append({
                    "product_id": product["id"],
                    "quantity": 1,
                    "comment": ""
                })

        return items

    def _add_items_to_cart(
        self,
        items: List[Dict[str, Any]],
        user_id: Optional[int],
        session_id: Optional[str]
    ) -> str:
        if not user_id:
            return (
                "🔐 Чтобы товары появились в корзине приложения, сначала войди в аккаунт "
                "во вкладке «Ещё». После входа я смогу добавлять позиции прямо в твою корзину."
            )

        PAIRINGS = {
            1: [8, 9, 10, 11],
            2: [8, 9],
            3: [8, 9, 10],
            4: [8, 9],
            5: [8, 9, 10, 11],
            6: [8, 9],
            7: [8, 9],
            8: [10, 11],
            9: [10, 11],
            10: [8, 9],
            11: [8, 9],
        }

        responses = []
        total = 0
        added_product_ids = []

        for item in items:
            result = self.add_to_cart(
                product_id=item["product_id"],
                quantity=item.get("quantity", 1),
                comment=item.get("comment", ""),
                user_id=user_id,
                session_id=session_id
            )

            if result["success"]:
                responses.append(
                    f"✅ {result['product_name']} ({item.get('quantity', 1)} шт.) добавлено в корзину! Сумма: {result['price']}₽"
                )
                total += result["price"]
                added_product_ids.append(item["product_id"])
            else:
                responses.append(f"❌ Ошибка: {result.get('error', 'Не удалось добавить товар')}")

        if len(responses) > 1:
            responses.append(f"\n💰 Итого за добавленные товары: {total}₽")

        if added_product_ids and len(responses) <= 3:
            base_id = added_product_ids[0]
            pairing_ids = PAIRINGS.get(base_id, [])
            suggested_ids = [pid for pid in pairing_ids if pid not in added_product_ids]

            if suggested_ids:
                suggest_names = {
                    8: ("Морс ягодный", 150),
                    9: ("Зеленый чай", 120),
                    10: ("Чизкейк Нью-Йорк", 250),
                    11: ("Тирамису", 300),
                }
                suggest_id = suggested_ids[0]
                if suggest_id in suggest_names:
                    name, price = suggest_names[suggest_id]
                    responses.append(f"🍽️ К этому отлично подойдёт «{name}» за {price}₽! Добавить?")

        return "\n".join(responses) if responses else "Товар добавлен в корзину!"

    def add_to_cart(self, product_id: int, quantity: int = 1, comment: Optional[str] = None, 
                    user_id: Optional[int] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {"success": False, "error": "Товар не найден"}
        cart = None
        if user_id:
            cart = self.db.query(Cart).filter(Cart.user_id == user_id).first()
            if not cart:
                cart = Cart(user_id=user_id)
                self.db.add(cart)
                self.db.flush()
        elif session_id:
            fake_user_id = hash(session_id) % 1000000 
            cart = self.db.query(Cart).filter(Cart.user_id == fake_user_id).first()
            if not cart:
                cart = Cart(user_id=fake_user_id)
                self.db.add(cart)
                self.db.flush()
        
        if not cart:
            return {"success": False, "error": "Корзина не найдена"}
        
        cart_item = self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
            CartItem.comment == comment
        ).first()
        
        if cart_item:
            cart_item.quantity += quantity
            if comment:
                cart_item.comment = comment
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                comment=comment
            )
            self.db.add(cart_item)
        
        self.db.commit()
        
        return {
            "success": True,
            "product_name": product.name,
            "quantity": cart_item.quantity,
            "price": product.price * cart_item.quantity
        }

    def _is_checkout_intent(self, message: str) -> bool:
        normalized = self._normalize_text(message)
        triggers = (
            "оформи заказ",
            "оформить заказ",
            "хочу оформить",
            "перейти к оплате",
            "готов оформить",
            "заказать это",
            "сделай заказ",
        )
        return any(trigger in normalized for trigger in triggers)

    def _is_checkout_cancel_intent(self, message: str) -> bool:
        normalized = self._normalize_text(message)
        return normalized in {
            "отмена", "отменить", "стоп", "не надо", "выход", "прекрати оформление"
        }

    def _looks_like_skip(self, message: str) -> bool:
        normalized = self._normalize_text(message)
        return normalized in {"нет", "не надо", "-", "без комментария", "без комментариев", "пропустить"}

    def _parse_payment_method(self, message: str) -> Optional[str]:
        normalized = self._normalize_text(message)
        if "сбп" in normalized:
            return PaymentMethod.sbp.value
        if "нал" in normalized or "курьеру" in normalized or "при получении" in normalized:
            return PaymentMethod.cash_on_delivery.value
        if "карт" in normalized or "card" in normalized:
            return PaymentMethod.credit_card.value
        return None

    def _get_cart_summary(self, user_id: Optional[int]) -> Optional[Dict[str, Any]]:
        if not user_id:
            return None

        cart = CartRepository(self.db).get_cart_by_user_id(user_id)
        if not cart or not cart.items:
            return None

        items = []
        total = 0.0
        for item in cart.items:
            subtotal = item.product.price * item.quantity
            total += subtotal
            items.append({
                "name": item.product.name,
                "quantity": item.quantity,
                "subtotal": subtotal,
                "comment": item.comment,
            })
        return {"items": items, "total": total}

    def _format_cart_summary(self, user_id: Optional[int]) -> str:
        summary = self._get_cart_summary(user_id)
        if not summary:
            return "Корзина пуста."

        lines = ["Сейчас в корзине:"]
        for item in summary["items"]:
            comment_suffix = f" [{item['comment']}]" if item["comment"] else ""
            lines.append(
                f"- {item['name']} x{item['quantity']} — {item['subtotal']:.0f} ₽{comment_suffix}"
            )
        lines.append(f"Итого: {summary['total']:.0f} ₽")
        return "\n".join(lines)

    def _ensure_checkout_prerequisites(
        self,
        user_id: Optional[int],
    ) -> Optional[str]:
        if not user_id:
            return (
                "Чтобы оформить заказ через консультанта, сначала войди в аккаунт во вкладке «Ещё». "
                "После входа я смогу оформить заказ из твоей корзины."
            )

        summary = self._get_cart_summary(user_id)
        if not summary:
            return "Сейчас корзина пустая. Сначала добавь товары, а потом я помогу оформить заказ."
        return None

    def _seed_checkout_state(self, state: ChatCheckoutState, user: Optional[User]) -> None:
        if not user:
            self.db.commit()
            self.db.refresh(state)
            return

        if not state.customer_phone and user.phone:
            state.customer_phone = user.phone
        if not state.customer_name:
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            state.customer_name = full_name or user.login
        self.db.commit()
        self.db.refresh(state)

    def _get_checkout_prompt(self, state: ChatCheckoutState) -> str:
        if not state.delivery_address:
            return "Укажи адрес доставки одним сообщением."
        if not state.payment_method:
            return (
                "Какой способ оплаты выбрать?\n"
                "- наличными\n"
                "- картой\n"
                "- СБП"
            )
        if not state.customer_name:
            return "На какое имя оформить заказ?"
        if not state.customer_phone:
            return "Укажи телефон для связи."
        if state.order_comment is None:
            return "Нужен комментарий к заказу? Если нет, напиши «нет»."
        return self._build_checkout_confirmation(state)

    def _build_checkout_confirmation(self, state: ChatCheckoutState) -> str:
        cart_summary = self._format_cart_summary(state.user_id)
        payment_label = self.PAYMENT_METHOD_LABELS.get(state.payment_method or "", state.payment_method or "-")
        comment = state.order_comment or "без комментария"
        return (
            f"{cart_summary}\n\n"
            f"Проверь данные заказа:\n"
            f"Адрес: {state.delivery_address}\n"
            f"Оплата: {payment_label}\n"
            f"Имя: {state.customer_name}\n"
            f"Телефон: {state.customer_phone}\n"
            f"Комментарий: {comment}\n\n"
            "Если всё верно, напиши «подтверждаю». Если хочешь отменить оформление, напиши «отмена»."
        )

    def _create_order_from_checkout(self, state: ChatCheckoutState) -> str:
        if not state.user_id:
            return "Не удалось определить пользователя для оформления заказа."

        cart_repo = CartRepository(self.db)
        cart = cart_repo.get_cart_by_user_id(state.user_id)
        if not cart or not cart.items:
            self._delete_checkout_state(state)
            return "Корзина стала пустой, поэтому оформить заказ не получилось."

        items = [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.product.price,
                "comment": item.comment,
                "special_requests": None,
            }
            for item in cart.items
        ]

        repo = OrderRepository(self.db)
        service = OrderService(self.db)
        order = repo.create_order(
            user_id=state.user_id,
            total_price=sum(item["price"] * item["quantity"] for item in items),
            delivery_address=state.delivery_address or "",
            delivery_comment=None,
            delivery_time=None,
            delivery_lat=None,
            delivery_lng=None,
            customer_phone=state.customer_phone,
            customer_name=state.customer_name,
            order_comment=state.order_comment or None,
            payment_method=state.payment_method or PaymentMethod.cash_on_delivery.value,
            items=items,
        )
        order = service.process_fake_payment(order)
        cart_repo.clear_cart(cart)
        order_id = order.id
        self._delete_checkout_state(state)
        return (
            f"Заказ #{order_id} оформлен.\n"
            f"Адрес: {order.delivery_address}\n"
            f"Оплата: {self.PAYMENT_METHOD_LABELS.get(order.payment_method.value, order.payment_method.value)}\n"
            "Заказ уже передан в обработку."
        )

    def _advance_checkout(
        self,
        message: str,
        user_id: Optional[int],
        session_id: Optional[str],
    ) -> Optional[str]:
        state = self._get_checkout_state(session_id)
        if not state:
            return None

        if self._is_checkout_cancel_intent(message):
            self._delete_checkout_state(state)
            return "Оформление заказа отменено. Если захочешь продолжить позже, просто напиши «оформить заказ»."

        if not state.delivery_address:
            state.delivery_address = message.strip()
        elif not state.payment_method:
            payment_method = self._parse_payment_method(message)
            if not payment_method:
                return (
                    "Не понял способ оплаты. Напиши один из вариантов:\n"
                    "- наличными\n"
                    "- картой\n"
                    "- СБП"
                )
            state.payment_method = payment_method
        elif not state.customer_name:
            state.customer_name = message.strip()
        elif not state.customer_phone:
            state.customer_phone = message.strip()
        elif state.order_comment is None:
            state.order_comment = "" if self._looks_like_skip(message) else message.strip()
        else:
            if self._is_affirmative(message) or "подтвержда" in self._normalize_text(message):
                return self._create_order_from_checkout(state)
            return (
                "Чтобы создать заказ, напиши «подтверждаю». "
                "Если нужно прервать оформление, напиши «отмена»."
            )

        self.db.commit()
        self.db.refresh(state)
        return self._get_checkout_prompt(state)

    def _start_checkout(
        self,
        user_id: Optional[int],
        session_id: Optional[str],
    ) -> str:
        blocker = self._ensure_checkout_prerequisites(user_id)
        if blocker:
            return blocker

        state = self._get_or_create_checkout_state(user_id, session_id)
        user = self.db.query(User).filter(User.id == user_id).first() if user_id else None
        self._seed_checkout_state(state, user)
        return self._get_checkout_prompt(state)

    def _extract_order_id_from_message(self, message: str) -> Optional[int]:
        if not message:
            return None

        patterns = [
            r"(?:заказ(?:а|у|ом)?\s*[№#]?\s*)(\d+)\b",
            r"[№#]\s*(\d+)\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return int(match.group(1))
        return None

    def _estimate_support_eta(self, order: Order) -> Optional[str]:
        now = datetime.now(timezone.utc)
        created_at = order.created_at
        picked_up_at = order.picked_up_at

        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if picked_up_at and picked_up_at.tzinfo is None:
            picked_up_at = picked_up_at.replace(tzinfo=timezone.utc)

        elapsed_from_created = max(0, int((now - created_at).total_seconds() // 60)) if created_at else None
        elapsed_from_pickup = max(0, int((now - picked_up_at).total_seconds() // 60)) if picked_up_at else None

        if order.status in {OrderStatus.created, OrderStatus.paid}:
            remaining = 30
            if elapsed_from_created is not None:
                remaining = max(10, 35 - elapsed_from_created)
            return f"ориентировочно {remaining}-{remaining + 10} мин."

        if order.status == OrderStatus.cooking:
            remaining = 20
            if elapsed_from_created is not None:
                remaining = max(10, 30 - elapsed_from_created)
            return f"ориентировочно {remaining}-{remaining + 10} мин."

        if order.status == OrderStatus.ready:
            return "ориентировочно 10-20 мин."

        if order.status == OrderStatus.delivering:
            remaining = 15
            if elapsed_from_pickup is not None:
                remaining = max(5, 20 - elapsed_from_pickup)
            return f"ориентировочно {remaining}-{remaining + 10} мин."

        return None

    def _find_support_order(self, user_id: int, requested_order_id: Optional[int]) -> tuple[Optional[Order], Optional[str]]:
        if requested_order_id is not None:
            order = (
                self.db.query(Order)
                .filter(Order.id == requested_order_id, Order.user_id == user_id)
                .first()
            )
            if not order:
                return None, f"Заказ #{requested_order_id} не найден среди заказов этого пользователя."
            return order, None

        active_statuses = [
            OrderStatus.created,
            OrderStatus.paid,
            OrderStatus.cooking,
            OrderStatus.ready,
            OrderStatus.delivering,
        ]
        active_order = (
            self.db.query(Order)
            .filter(Order.user_id == user_id, Order.status.in_(active_statuses))
            .order_by(Order.created_at.desc())
            .first()
        )
        if active_order:
            return active_order, None

        latest_order = (
            self.db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .first()
        )
        return latest_order, None

    def _format_support_order_summary(self, order: Order) -> str:
        status_label = self.SUPPORT_STATUS_LABELS.get(order.status, order.status.value)
        eta = self._estimate_support_eta(order)
        parts = [
            f"Заказ #{order.id}",
            f"статус: {status_label}",
            f"адрес доставки: {order.delivery_address}",
            f"сумма: {order.total_price} ₽",
        ]
        if order.delivery_time:
            parts.append(f"пожелание по времени: {order.delivery_time}")
        if eta:
            parts.append(f"примерное ожидание: {eta}")
        return ", ".join(parts)

    def _build_support_context(self, user_id: Optional[int], message: str) -> str:
        lines = [
            "Пиццерия Piazza Pizza",
            "Адрес: ул. Кирова, 1, Калуга",
            "Часы работы: 10:00-23:00",
            "Доставка: обычно около 30 минут",
            "Самовывоз доступен из пиццерии по адресу выше",
            "Оплата: наличные, карта, онлайн",
        ]

        if not user_id:
            lines.append("Пользователь не авторизован: персональные данные по заказам недоступны.")
            return "\n".join(lines)

        requested_order_id = self._extract_order_id_from_message(message)
        target_order, lookup_note = self._find_support_order(user_id, requested_order_id)

        if lookup_note:
            lines.append(lookup_note)

        if target_order:
            if requested_order_id is not None:
                lines.append("Пользователь спросил про конкретный заказ:")
            else:
                lines.append("Самый актуальный заказ пользователя:")
            lines.append(f"- {self._format_support_order_summary(target_order)}")

        recent_orders = (
            self.db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(3)
            .all()
        )
        if not recent_orders:
            lines.append("У пользователя пока нет оформленных заказов.")
            return "\n".join(lines)

        lines.append("Последние заказы пользователя:")
        for order in recent_orders:
            status_label = self.SUPPORT_STATUS_LABELS.get(order.status, order.status.value)
            eta = self._estimate_support_eta(order)
            eta_suffix = f", ожидание: {eta}" if eta else ""
            lines.append(
                f"- Заказ #{order.id}: статус {status_label}, сумма {order.total_price} ₽{eta_suffix}"
            )
        return "\n".join(lines)

    def _detect_support_escalation(self, content: str) -> tuple[bool, str]:
        normalized = (content or "").strip()
        if normalized.upper().startswith("ESCALATE:"):
            return True, normalized.split(":", 1)[1].strip()
        return False, normalized

    def _create_support_ticket(
        self,
        user_id: Optional[int],
        session_id: Optional[str],
        user_message: str,
        agent_response: str,
    ) -> Optional[int]:
        if not user_id:
            return None

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        source = "telegram" if session_id and "tg_" in session_id else "app"
        ticket = SupportTicketService(self.db).create_ticket(
            user=user,
            user_message=user_message,
            agent_response=agent_response,
            source=source,
        )
        return ticket.id

    def _build_system_prompt(
        self,
        agent_type: str,
        menu_json: str,
        menu_ids: str,
        user_id: Optional[int],
        message: str,
    ) -> str:
        if agent_type == "support":
            support_context = self._build_support_context(user_id, message)
            return f"""You are SUPPORT WOKI — a dedicated technical support AI agent for Piazza Pizza.
You are a separate support agent, not a food consultant.
Always respond in Russian.

SUPPORT TASKS:
- answer where the order is and explain current status
- answer how to get to the pizzeria and where pickup works
- answer about working hours, delivery, payment, and pickup
- help with delays, order issues, and next steps
- if support context contains a relevant user order, answer based on that order first
- never say that another user's order belongs to the current user
- never ask for the order number again if support context already contains the requested order
- when ETA is approximate, say that it is an estimate, not an exact promise
- if the user asks to choose food, briefly redirect to the consultant agent
- if the problem clearly needs a human, start the answer with `ESCALATE:` and then briefly explain why

SUPPORT CONTEXT:
{support_context}

RULES:
- be calm, clear, and practical
- do not invent exact courier location or ETA if it is unknown
- if there is not enough data, say exactly what is missing
- do not use cart tools
- do not behave like a sales assistant
"""

        return f"""You are WOKI — a friendly and slightly humorous assistant
of Piazza Pizza in Kaluga, Russia. You love pizza and are passionate about food.
Address: Kirova st. 1. Hours: 10:00-23:00. Delivery: 30 min or free.
Always respond in Russian with emoji.

PERSONALITY:
- Warm, friendly, like talking to a good friend
- Occasionally make light pizza jokes or food puns
- Show genuine enthusiasm when recommending dishes
- If user seems hungry — empathize: "Понимаю, когда хочется есть — это срочно! 🍕"
- Use casual Russian (ты, not вы) unless user uses formal tone
- If user says thanks — respond warmly, not robotically

MENU:
{menu_json}

CART IDs — ИСПОЛЬЗУЙ ТОЛЬКО ЭТИ ID, НЕ ПЕРЕПУТАЙ:
{menu_ids}

CRITICAL:
- Тирамису = id 11, Чизкейк Нью-Йорк = id 10 — это РАЗНЫЕ товары
- Всегда сверяй название с CART IDs списком выше перед вызовом add_to_cart
- Никогда не путай десерты между собой
- Никогда не показывай пользователю id товаров и не упоминай служебные tool arguments в ответе

RULES:
- Use calories_total for calorie questions (not calories per 100g)
- Match items by meaning using CART IDs list — 'тирамису'=id 11, 'чизкейк'=id 10
- Only answer questions about the pizzeria
- If item not in menu — say so warmly and suggest alternative
- Never say "Извините, я могу помочь только..." — instead redirect naturally

CART: When user wants to add item — find it in CART IDs list above,
get its exact id, call add_to_cart.
If multiple items added — calculate and show total sum at the end."""

    def generate_response(
        self,
        message: str,
        context: List[dict],
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        agent_type: str = "consultant",
    ) -> str:

        try:
            menu_json = self.get_menu_context()
            
            menu_list = json.loads(menu_json)
            menu_ids = "\n".join([f"- {p['name']} = id {p['id']}" for p in menu_list])

            if agent_type == "consultant":
                active_checkout_response = self._advance_checkout(message, user_id, session_id)
                if active_checkout_response:
                    return active_checkout_response

                if self._is_checkout_intent(message):
                    return self._start_checkout(user_id, session_id)

                calorie_combo_response = self._build_calorie_combo_response(message, menu_list)
                if calorie_combo_response:
                    return calorie_combo_response

                parsed_items = self._extract_items_from_message(message, menu_list)
                if parsed_items:
                    return self._add_items_to_cart(parsed_items, user_id, session_id)

                suggested_items = self._extract_suggested_item_from_context(message, context, menu_list)
                if suggested_items:
                    return self._add_items_to_cart(suggested_items, user_id, session_id)

            system_prompt = self._build_system_prompt(
                agent_type=agent_type,
                menu_json=menu_json,
                menu_ids=menu_ids,
                user_id=user_id,
                message=message,
            )

            messages = [{"role": "system", "content": system_prompt}]

            # контекст (последние 5 сообщений)
            for msg in context[-5:]:
                messages.append({"role": "user", "content": msg["message"]})
                messages.append({"role": "assistant", "content": msg["response"]})

            # текущее сообщение
            messages.append({"role": "user", "content": message})

            result = ollama_service.send_message(
                messages=messages,
                temperature=0.7,
                tools=CART_TOOLS if agent_type == "consultant" else None
            )

            if agent_type == "consultant" and result.get("tool_calls"):
                return self._handle_tool_calls(result["tool_calls"], user_id, session_id)

            content = self._sanitize_assistant_response(result.get("content", ""))
            if agent_type == "support":
                should_escalate, cleaned_content = self._detect_support_escalation(content)
                if should_escalate:
                    ticket_id = self._create_support_ticket(user_id, session_id, message, cleaned_content)
                    if ticket_id:
                        return (
                            f"Я не могу точно ответить на этот вопрос. Ваше обращение перенаправлено администратору "
                            f"под номером #{ticket_id}. Как только администратор ответит, мы отправим ответ вам."
                        )
                    return (
                        "Чтобы передать вопрос живому администратору, нужно писать из авторизованного аккаунта "
                        "или из привязанного Telegram."
                    )
                return cleaned_content

            return content

        except Exception as e:
            import traceback
            print(f"ОШИБКА generate_response: {e}")
            traceback.print_exc()
            return self._fallback_response(message)

    def _handle_tool_calls(self, tool_calls: List[Dict], user_id: Optional[int], session_id: Optional[str]) -> str:
        parsed_items = []

        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            func_name = function.get("name")
            func_args = function.get("arguments", {})

            if func_name == "add_to_cart":
                product_id = func_args.get("product_id")
                quantity = func_args.get("quantity", 1)
                comment = func_args.get("comment", "")

                if product_id:
                    parsed_items.append({
                        "product_id": product_id,
                        "quantity": quantity,
                        "comment": comment
                    })

        return self._add_items_to_cart(parsed_items, user_id, session_id)

    def _fallback_response(self, message: str) -> str:
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['пицц', 'вкусн', 'порекоменд']):
            return "Привет! Я WOKI, твой помощник Piazza Pizza! 🍕\n\nРекомендую «Четыре сыра» — моцарелла, пармезан, чеддер, блю чиз (620₽).\n\nДобавить в корзину?"
        
        if any(word in message_lower for word in ['напитк', 'пить']):
            return "Из напитков: 🥤 Морс ягодный (150₽), 🍵 Зеленый чай (120₽). Добавить?"
        
        if any(word in message_lower for word in ['десерт']):
            return "Десерты: 🍰 Чизкейк (250₽), 🧁 Тирамису (300₽). Хочешь попробовать?"
        
        if any(word in message_lower for word in ['привет']):
            return "Привет! Я WOKI из Piazza Pizza! 🍕 Спрашивай о меню — помогу выбрать!"
        
        if any(word in message_lower for word in ['доставк', 'время']):
            return "Доставка 30 минут или бесплатно! 🚀 Работаем 10:00-23:00."
        
        return "Я могу помочь только с вопросами о нашем меню и доставке пиццы 🍕 Спрашивай!"
