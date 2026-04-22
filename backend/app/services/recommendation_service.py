from __future__ import annotations

from collections import Counter, defaultdict
import json

from sqlalchemy.orm import Session, joinedload

from ..models.order import Order, OrderStatus
from ..models.orderItem import OrderItem
from ..models.products import Product
from .ollama_service import ollama_service


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def _product_type(self, product: Product) -> str:
        category = (product.category.name if product.category else "").lower()
        name = (product.name or "").lower()

        if any(keyword in category for keyword in ["напит", "drink"]) or any(keyword in name for keyword in ["кола", "чай", "морс", "сок", "вода"]):
            return "drink"
        if any(keyword in category for keyword in ["десерт", "dessert"]) or any(keyword in name for keyword in ["чизкейк", "тирамису", "десерт"]):
            return "dessert"
        return "main"

    def _normalize_reason(self, product_id: int, reason: str, main_ids: set[int], addon_ids: set[int]) -> str:
        clean_reason = (reason or "").strip()
        if clean_reason:
            return clean_reason
        if product_id in main_ids:
            return "Вы часто заказываете эту позицию."
        if product_id in addon_ids:
            return "Эта позиция хорошо дополнит ваши основные блюда в текущей подборке."
        return "Подходит к вашему обычному выбору."

    def _validate_suggestions_mix(self, suggestions: list[dict], product_map: dict[int, Product]) -> bool:
        if len(suggestions) != 3:
            return False

        type_counts: Counter[str] = Counter()
        pizza_count = 0
        burger_count = 0

        for item in suggestions:
            product = product_map.get(item["product_id"])
            if not product:
                return False

            product_type = self._product_type(product)
            type_counts[product_type] += 1

            category = (product.category.name if product.category else "").lower()
            name = (product.name or "").lower()
            if "пицц" in category or "pizza" in category or "пицц" in name:
                pizza_count += 1
            if "бургер" in category or "burger" in category or "бургер" in name:
                burger_count += 1

        if type_counts["drink"] >= 2:
            return False
        if type_counts["dessert"] >= 2:
            return False
        if pizza_count >= 3:
            return False
        if burger_count >= 3:
            return False
        return True

    def build_for_user(self, user_id: int) -> tuple[str, list[dict]]:
        orders = (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(
                Order.user_id == user_id,
                Order.status.in_([OrderStatus.paid, OrderStatus.cooking, OrderStatus.ready, OrderStatus.delivering, OrderStatus.completed]),
            )
            .order_by(Order.created_at.desc())
            .limit(20)
            .all()
        )

        if not orders:
            fallback_products = (
                self.db.query(Product)
                .filter(Product.is_available == 1)
                .order_by(Product.id.asc())
                .limit(3)
                .all()
            )
            suggestions = [
                {
                    "product_id": product.id,
                    "name": product.name,
                    "reason": "Популярная стартовая рекомендация для нового клиента",
                }
                for product in fallback_products
            ]
            return "Ты у нас пока без истории заказов. Могу предложить начать с самых базовых и популярных позиций.", suggestions

        product_counter: Counter[int] = Counter()
        product_names: dict[int, str] = {}
        categories: Counter[str] = Counter()
        hour_counter: Counter[str] = Counter()
        combos: defaultdict[tuple[int, ...], int] = defaultdict(int)

        for order in orders:
            if order.created_at:
                hour_counter["evening" if order.created_at.hour >= 18 else "day"] += 1

            combo = []
            for item in order.items:
                product_counter[item.product_id] += item.quantity
                combo.append(item.product_id)
                if item.product:
                    product_names[item.product_id] = item.product.name
                    if item.product.category:
                        categories[item.product.category.name] += item.quantity
            if combo:
                combos[tuple(sorted(set(combo)))] += 1

        ordered_favorites = [product_id for product_id, _ in product_counter.most_common(10)]
        products, product_map, main_ids, addon_ids = self._build_candidate_products(ordered_favorites, categories)
        favorite_period = "вечером" if hour_counter.get("evening", 0) >= hour_counter.get("day", 0) else "днём"

        products_payload = [
            {
                "product_id": product.id,
                "name": product.name,
                "category": product.category.name if product.category else "Другое",
                "price": product.price,
                "times_ordered": product_counter.get(product.id, 0),
            }
            for product in products
        ]

        history_payload = {
            "favorite_period": favorite_period,
            "favorite_categories": categories.most_common(3),
            "favorite_products": [
                {"product_id": product_id, "name": product_names.get(product_id, str(product_id)), "times_ordered": count}
                for product_id, count in product_counter.most_common(5)
            ],
            "common_combos": [{"product_ids": list(combo), "times": count} for combo, count in sorted(combos.items(), key=lambda item: item[1], reverse=True)[:3]],
            "candidate_products": products_payload,
            "required_main_product_ids": main_ids,
            "required_addon_product_ids": addon_ids,
        }

        llm_message, llm_suggestions = self._build_with_llm(history_payload, product_map)
        if len(llm_suggestions) == 3:
            return llm_message, llm_suggestions

        suggestions = []
        for product_id in main_ids[:2]:
            product = product_map.get(product_id)
            if not product:
                continue
            suggestions.append(
                {
                    "product_id": product.id,
                    "name": product.name,
                    "reason": "Вы часто выбираете эту позицию.",
                }
            )
        if addon_ids:
            addon = product_map.get(addon_ids[0])
            if addon:
                suggestions.append(
                    {
                        "product_id": addon.id,
                        "name": addon.name,
                        "reason": "Может хорошо дополнить ваш обычный выбор.",
                    }
                )
        return f"Обычно ты заказываешь похожие позиции {favorite_period}. Хочешь быстро повторить заказ?", suggestions[:3]

    def _build_candidate_products(self, favorite_ids: list[int], categories: Counter[str]) -> tuple[list[Product], dict[int, Product], list[int], list[int]]:
        favorite_products = []
        if favorite_ids:
            favorite_products = (
                self.db.query(Product)
                .filter(Product.id.in_(favorite_ids))
                .all()
            )

        favorite_map = {product.id: product for product in favorite_products}
        ordered_favorites = [favorite_map[product_id] for product_id in favorite_ids if product_id in favorite_map]

        main_products = [product for product in ordered_favorites if self._product_type(product) == "main"]
        other_products = [product for product in ordered_favorites if self._product_type(product) != "main"]
        selected_main = main_products[:2]
        if len(selected_main) < 2:
            for product in other_products:
                if len(selected_main) >= 2:
                    break
                if product.id not in {item.id for item in selected_main}:
                    selected_main.append(product)

        extra_candidates = (
            self.db.query(Product)
            .filter(Product.is_available == 1, ~Product.id.in_(favorite_ids or [0]))
            .order_by(Product.id.asc())
            .limit(20)
            .all()
        )

        favorite_category_names = {name for name, _ in categories.most_common(3)}
        complementary = []
        others = []
        for product in extra_candidates:
            category_name = product.category.name if product.category else "Другое"
            if self._product_type(product) != "main" and category_name not in favorite_category_names:
                complementary.append(product)
            else:
                others.append(product)

        final_products: list[Product] = []
        seen_ids: set[int] = set()
        main_ids: list[int] = []
        addon_ids: list[int] = []

        for product in selected_main:
            if product.id not in seen_ids:
                final_products.append(product)
                seen_ids.add(product.id)
                main_ids.append(product.id)

        for bucket in (complementary, others, ordered_favorites):
            for product in bucket:
                if len(addon_ids) >= 4:
                    break
                if product.id in seen_ids:
                    continue
                if self._product_type(product) == "main":
                    continue
                final_products.append(product)
                seen_ids.add(product.id)
                addon_ids.append(product.id)

        for bucket in (others, ordered_favorites):
            for product in bucket:
                if len(final_products) >= 6:
                    break
                if product.id not in seen_ids:
                    final_products.append(product)
                    seen_ids.add(product.id)

        product_map = {product.id: product for product in final_products}
        return final_products, product_map, main_ids, addon_ids

    def _build_with_llm(self, history_payload: dict, product_map: dict[int, Product]) -> tuple[str, list[dict]]:
        prompt = (
            "Ты агент персональных рекомендаций пиццерии.\n"
            "На основе истории заказов сформируй короткое персональное сообщение и ровно 3 рекомендации.\n"
            "Ты обязан вернуть ровно 3 разных товара в массиве suggestions, не меньше и не больше.\n"
            "Обращайся к клиенту только на 'вы'.\n"
            "Рекомендации должны быть персональными.\n"
            "Первые 2 рекомендации должны быть из required_main_product_ids — это часто заказываемые основные блюда клиента.\n"
            "Третья рекомендация должна быть из required_addon_product_ids — это уместное дополнение к первым двум.\n"
            "Не делайте третью рекомендацию основным блюдом, если есть доступные дополнения.\n"
            "Нельзя рекомендовать 3 пиццы.\n"
            "Нельзя рекомендовать 3 бургера.\n"
            "Нельзя рекомендовать одновременно 2 напитка.\n"
            "Нельзя рекомендовать одновременно 2 десерта.\n"
            "Набор должен быть разнообразным: два основных товара и одно уместное дополнение.\n"
            "В сообщении не перечисляй весь список возможных напитков, десертов или других товаров.\n"
            "Упоминай только две основные позиции клиента и один конкретный дополнительный товар, который вы рекомендуете сейчас.\n"
            "Для первых двух основных товаров не расписывай подробные причины: достаточно короткой формулировки в духе 'Вы часто заказываете эту позицию'.\n"
            "Подробное содержательное объяснение дай только для третьего, дополнительного товара.\n"
            "У всех трёх товаров поле reason должно быть непустым.\n"
            "Все 3 product_id должны быть разными.\n"
            "Отвечай строго JSON-объектом формата:\n"
            '{"message":"...","suggestions":[{"product_id":1,"reason":"..."}]}\n'
            "Используй только product_id из candidate_products.\n"
            "Не выдумывай товары.\n\n"
            f"{json.dumps(history_payload, ensure_ascii=False)}"
        )
        try:
            main_ids = set(history_payload.get("required_main_product_ids", []))
            addon_ids = set(history_payload.get("required_addon_product_ids", []))

            messages = [
                {"role": "system", "content": "Ты AI-агент персональных рекомендаций для сервиса доставки пиццы. Обращайся к клиенту только на 'вы'. Отвечай строго JSON без markdown."},
                {"role": "user", "content": prompt},
            ]

            for attempt in range(2):
                result = ollama_service.send_message(
                    messages=messages,
                    temperature=0.2,
                )
                payload = json.loads((result.get("content") or "").strip())
                suggestions: list[dict] = []
                used_ids: set[int] = set()

                for item in payload.get("suggestions", [])[:3]:
                    product_id = item.get("product_id")
                    if product_id in used_ids:
                        continue
                    product = product_map.get(product_id)
                    if not product:
                        continue
                    suggestions.append(
                        {
                            "product_id": product.id,
                            "name": product.name,
                            "reason": self._normalize_reason(product_id, item.get("reason") or "", main_ids, addon_ids),
                        }
                    )
                    used_ids.add(product_id)

                if self._validate_suggestions_mix(suggestions, product_map):
                    return payload.get("message", "Подобрал персональные рекомендации на основе ваших заказов."), suggestions

                if attempt == 0:
                    messages.append(
                        {
                            "role": "user",
                            "content": "Предыдущий набор нарушил правила. Соберите новый JSON-ответ строго из 3 разных товаров: без двух напитков, без двух десертов, без трех пицц и без трех бургеров.",
                        }
                    )

            return "", []
        except Exception:
            return "", []
