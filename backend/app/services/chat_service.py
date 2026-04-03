from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from ..models.chat_message import ChatMessage
from ..models.products import Product
from ..models.cart import Cart
from ..models.cartItem import CartItem
from ..services.ollama_service import ollama_service, CART_TOOLS


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_history(self, user_id: Optional[int] = None, session_id: Optional[str] = None, limit: int = 20) -> List[ChatMessage]:
        query = self.db.query(ChatMessage)
        
        if user_id:
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
            CartItem.product_id == product_id
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
        PAIRINGS = {
            1: [8,9,10,11],  # Четыре сыра → напитки/десерты
            2: [8,9],        # Мясная → напитки
            3: [8,9,10],     # Гавайская → напитки/десерты
            4: [8,9],        # Пепперони → напитки
            5: [8,9,10,11],  # Маргарита → напитки/десерты
            6: [8,9],        # Дабл Биф → напитки
            7: [8,9],        # Чикен Бургер → напитки
            8: [10,11],      # Морс → десерты
            9: [10,11],      # Чай → десерты
            10: [8,9],       # Чизкейк → напитки
            11: [8,9],       # Тирамису → напитки
        }
        
        responses = []
        total = 0
        added_product_ids = []

        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            func_name = function.get("name")
            func_args = function.get("arguments", {})

            if func_name == "add_to_cart":
                product_id = func_args.get("product_id")
                quantity = func_args.get("quantity", 1)
                comment = func_args.get("comment", "")

                if product_id:
                    result = self.add_to_cart(
                        product_id=product_id,
                        quantity=quantity,
                        comment=comment,
                        user_id=user_id,
                        session_id=session_id
                    )

                    if result["success"]:
                        responses.append(
                            f"✅ {result['product_name']} ({result['quantity']} шт.) добавлено в корзину! Сумма: {result['price']}₽"
                        )
                        total += result['price']
                        added_product_ids.append(product_id)
                    else:
                        responses.append(f"❌ Ошибка: {result.get('error', 'Не удалось добавить товар')}")

        # если добавили больше 1 товара — показываем общую сумму
        if len(responses) > 1:
            responses.append(f"\n💰 Итого: {total}₽")

        if added_product_ids and len(responses) <= 3:
            base_id = added_product_ids[0]
            pairing_ids = PAIRINGS.get(base_id, [])
            
            suggested_ids = [pid for pid in pairing_ids if pid not in added_product_ids]
            
            if suggested_ids:
                suggest_id = suggested_ids[0]
                from ..models.products import Product
                from sqlalchemy.orm import Session
                suggest_names = {
                    8: ("Морс ягодный", 150),
                    9: ("Зеленый чай", 120),
                    10: ("Чизкейк Нью-Йорк", 250),
                    11: ("Тирамису", 300),
                }
                if suggest_id in suggest_names:
                    name, price = suggest_names[suggest_id]
                    responses.append(f"🍽️ К этому отлично подойдёт «{name}» за {price}₽! Добавить?")

        return "\n".join(responses) if responses else "Товар добавлен в корзину!"

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
