from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import re
from ..models.chat_message import ChatMessage
from ..models.products import Product
from ..models.cart import Cart
from ..models.cartItem import CartItem
from ..services.ollama_service import ollama_service, CART_TOOLS


class ChatService:
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
        
        if user_id:
            query = query.filter(ChatMessage.user_id == user_id)п
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

    def clear_history(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> int:
        query = self.db.query(ChatMessage)
        
        if user_id:
            query = query.filter(ChatMessage.user_id == user_id)
        elif session_id:
            query = query.filter(ChatMessage.session_id == session_id)
        
        count = query.count()
        query.delete()
        self.db.commit()
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

    def generate_response(self, message: str, context: List[dict], user_id: Optional[int] = None, session_id: Optional[str] = None) -> str:

        try:
            menu_json = self.get_menu_context()
            
            menu_list = json.loads(menu_json)
            menu_ids = "\n".join([f"- {p['name']} = id {p['id']}" for p in menu_list])

            parsed_items = self._extract_items_from_message(message, menu_list)
            if parsed_items:
                return self._add_items_to_cart(parsed_items, user_id, session_id)

            suggested_items = self._extract_suggested_item_from_context(message, context, menu_list)
            if suggested_items:
                return self._add_items_to_cart(suggested_items, user_id, session_id)

            system_prompt = f"""You are WOKI — a friendly and slightly humorous assistant
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
                tools=CART_TOOLS
            )

            if result.get("tool_calls"):
                return self._handle_tool_calls(result["tool_calls"], user_id, session_id)

            return result.get("content", "")

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
