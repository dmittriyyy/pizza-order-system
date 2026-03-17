from app.database import SessionLocal, init_db, engine, Base
from app.models.users import User, UserRole, UserStatus
from app.models.category import Category
from app.models.products import Product
from app.services.auth_service import get_password_hash
import json

def seed_data():
    # Полная очистка и создание таблиц
    Base.metadata.drop_all(bind=engine)
    init_db()

    db = SessionLocal()
    try:
        # --- 1. КАТЕГОРИИ ---
        categories_data = {
            "pizza": Category(name="Пицца", slug="pizza"),
            "burgers": Category(name="Бургеры", slug="burgers"),
            "drinks": Category(name="Напитки", slug="drinks"),
            "desserts": Category(name="Десерты", slug="desserts")
        }
        db.add_all(categories_data.values())
        db.commit()

        # --- 2. ПРОДУКТЫ с фото, калориями и составом ---
        products_list = [
            # Пицца
            Product(
                name="Четыре сыра",
                description="Классическая итальянская пицца с четырьмя видами сыра: моцарелла, пармезан, чеддер и блю чиз. Идеальный баланс вкусов для настоящих ценителей.",
                slug="four-cheese",
                price=620.0,
                category_id=categories_data["pizza"].id,
                image_url="https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&h=300&fit=crop",
                calories=265,
                protein=12.5,
                fat=14.2,
                carbohydrates=24.8,
                weight=300,
                ingredients=["моцарелла", "пармезан", "чеддер", "блю чиз", "томатный соус", "тесто"],
                is_available=1
            ),
            Product(
                name="Мясная",
                description="Сытная пицца для настоящих мясоедов. Бекон, ветчина, пепперони и говядина — всё, что вы любите в одном блюде.",
                slug="meat-pizza",
                price=690.0,
                category_id=categories_data["pizza"].id,
                image_url="https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500&h=300&fit=crop",
                calories=285,
                protein=15.8,
                fat=16.5,
                carbohydrates=22.3,
                weight=350,
                ingredients=["бекон", "ветчина", "пепперони", "говядина", "моцарелла", "томатный соус", "тесто"],
                is_available=1
            ),
            Product(
                name="Гавайская",
                description="Сочетание курицы и ананаса создаёт уникальный сладко-солёный вкус. Поляризующая пицца, которую либо любят, либо ненавидят.",
                slug="hawaiian",
                price=580.0,
                category_id=categories_data["pizza"].id,
                image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&h=300&fit=crop",
                calories=245,
                protein=13.2,
                fat=10.5,
                carbohydrates=26.1,
                weight=320,
                ingredients=["курица", "ананасы", "моцарелла", "соус бешамель", "тесто"],
                is_available=1
            ),
            Product(
                name="Пепперони",
                description="Классика жанра. Острая пепперони с тягучей моцареллой и фирменным томатным соусом.",
                slug="pepperoni",
                price=590.0,
                category_id=categories_data["pizza"].id,
                image_url="https://images.unsplash.com/photo-1593560708920-6316e4e6d54e?w=500&h=300&fit=crop",
                calories=270,
                protein=14.0,
                fat=13.8,
                carbohydrates=23.5,
                weight=300,
                ingredients=["пепперони", "моцарелла", "томатный соус", "орегано", "тесто"],
                is_available=1
            ),
            Product(
                name="Маргарита",
                description="Самая простая и гениальная пицца. Только томаты, моцарелла и свежий базилик. Вкус Италии в каждом кусочке.",
                slug="margarita",
                price=520.0,
                category_id=categories_data["pizza"].id,
                image_url="https://images.unsplash.com/photo-1590947132387-155cc02f3212?w=500&h=300&fit=crop",
                calories=230,
                protein=10.5,
                fat=9.2,
                carbohydrates=28.0,
                weight=280,
                ingredients=["томаты сан-марцано", "моцарелла фиор ди латте", "базилик", "оливковое масло", "тесто"],
                is_available=1
            ),

            # Бургеры
            Product(
                name="Дабл Биф",
                description="Две сочные котлеты из мраморной говядины, карамелизированный лук, маринованные огурцы и фирменный соус на бриоши булочке.",
                slug="double-beef",
                price=450.0,
                category_id=categories_data["burgers"].id,
                image_url="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&h=300&fit=crop",
                calories=320,
                protein=18.5,
                fat=22.0,
                carbohydrates=15.2,
                weight=280,
                ingredients=["говядина мраморная", "булочка бриошь", "картофель фри", "лук карамелизированный", "огурцы маринованные", "фирменный соус"],
                is_available=1
            ),
            Product(
                name="Чикен Бургер",
                description="Хрустящее куриное филе в панировке, свежий салат, томаты и соус карри. Лёгкий, но сытный вариант.",
                slug="chicken-burger",
                price=320.0,
                category_id=categories_data["burgers"].id,
                image_url="https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=500&h=300&fit=crop",
                calories=280,
                protein=16.2,
                fat=14.5,
                carbohydrates=20.8,
                weight=250,
                ingredients=["куриное филе в панировке", "булочка", "салат айсберг", "томаты", "соус карри"],
                is_available=1
            ),

            # Напитки
            Product(
                name="Морс ягодный",
                description="Домашний морс из свежих ягод: клюква, брусника, малина. Без консервантов, только натуральные ингредиенты.",
                slug="berry-juice",
                price=150.0,
                category_id=categories_data["drinks"].id,
                image_url="https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500&h=300&fit=crop",
                calories=45,
                protein=0.5,
                fat=0.2,
                carbohydrates=10.5,
                weight=500,
                ingredients=["клюква", "брусника", "малина", "вода", "сахар"],
                is_available=1
            ),
            Product(
                name="Зеленый чай",
                description="Освежающий холодный чай с лимоном и мятой. Идеально дополняет любую пиццу.",
                slug="green-tea",
                price=120.0,
                category_id=categories_data["drinks"].id,
                image_url="https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=500&h=300&fit=crop",
                calories=25,
                protein=0.1,
                fat=0.0,
                carbohydrates=6.2,
                weight=500,
                ingredients=["зеленый чай", "лимон", "мята", "вода", "мёд"],
                is_available=1
            ),

            # Десерты
            Product(
                name="Чизкейк Нью-Йорк",
                description="Классический американский чизкейк с нежным творожным слоем и клубничным соусом. Тает во рту!",
                slug="cheesecake",
                price=250.0,
                category_id=categories_data["desserts"].id,
                image_url="https://images.unsplash.com/photo-1524351199678-941a58a3df50?w=500&h=300&fit=crop",
                calories=320,
                protein=6.5,
                fat=22.0,
                carbohydrates=24.5,
                weight=150,
                ingredients=["сливочный сыр", "печенье савоярди", "сливки", "яйца", "клубничный соус"],
                is_available=1
            ),
            Product(
                name="Тирамису",
                description="Изысканный итальянский десерт с маскарпоне, печеньем савоярди и эспрессо. Посыпан какао.",
                slug="tiramisu",
                price=300.0,
                category_id=categories_data["desserts"].id,
                image_url="https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500&h=300&fit=crop",
                calories=290,
                protein=5.8,
                fat=18.5,
                carbohydrates=26.2,
                weight=140,
                ingredients=["маскарпоне", "печенье савоярди", "эспрессо", "яйца", "какао", "сахар"],
                is_available=1
            ),
        ]
        db.add_all(products_list)

        # --- 3. ПОЛЬЗОВАТЕЛИ с хешированными паролями ---
        users_list = [
            User(first_name="Артём", last_name="Админов", login="admin_boss", password_hash=get_password_hash("pass_1"), role=UserRole.admin, email="admin@pizza.ru"),
            User(first_name="Мария", last_name="Кондитер", login="cook_maria", password_hash=get_password_hash("pass_2"), role=UserRole.cook),
            User(first_name="Виктор", last_name="Быстрый", login="courier_vic", password_hash=get_password_hash("pass_3"), role=UserRole.courier),
            User(first_name="Игорь", last_name="Клиент", login="user_igor", password_hash=get_password_hash("pass_4"), role=UserRole.client, status=UserStatus.active),
            User(first_name="Анна", last_name="Новичок", login="user_anna", password_hash=get_password_hash("pass_5"), role=UserRole.client, status=UserStatus.active),
        ]
        db.add_all(users_list)

        db.commit()
        print(f"🔥 Успех! Добавлено категорий: {len(categories_data)}, продуктов: {len(products_list)}, пользователей: {len(users_list)}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
