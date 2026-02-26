from app.database import SessionLocal, init_db, engine, Base
from app.models.users import User, UserRole, UserStatus
from app.models.category import Category
from app.models.products import Product

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

        # --- 2. ПРОДУКТЫ ---
        products_list = [
            # Пицца
            Product(name="Четыре сыра", description="Моцарелла, пармезан, чеддер, блю чиз", slug="four-cheese", price=620.0, category_id=categories_data["pizza"].id),
            Product(name="Мясная", description="Бекон, ветчина, пепперони, говядина", slug="meat-pizza", price=690.0, category_id=categories_data["pizza"].id),
            Product(name="Гавайская", description="Курица, ананас, соус бешамель", slug="hawaiian", price=580.0, category_id=categories_data["pizza"].id),
            
            # Бургеры
            Product(name="Дабл Биф", description="Две котлеты из говядины, карамелизированный лук", slug="double-beef", price=450.0, category_id=categories_data["burgers"].id),
            Product(name="Чикен Бургер", description="Куриное филе в панировке, соус карри", slug="chicken-burger", price=320.0, category_id=categories_data["burgers"].id),
            
            # Напитки
            Product(name="Морс ягодный", description="Домашний морс, 0.5л", slug="berry-juice", price=150.0, category_id=categories_data["drinks"].id),
            Product(name="Зеленый чай", description="Холодный чай с лимоном, 0.5л", slug="green-tea", price=120.0, category_id=categories_data["drinks"].id),
            
            # Десерты
            Product(name="Чизкейк Нью-Йорк", description="Классический творожный десерт", slug="cheesecake", price=250.0, category_id=categories_data["desserts"].id),
            Product(name="Тирамису", description="Итальянский десерт с маскарпоне", slug="tiramisu", price=300.0, category_id=categories_data["desserts"].id),
        ]
        db.add_all(products_list)

        # --- 3. ПОЛЬЗОВАТЕЛИ ---
        users_list = [
            User(first_name="Артём", last_name="Админов", login="admin_boss", password_hash="pass_1", role=UserRole.admin, email="admin@pizza.ru"),
            User(first_name="Мария", last_name="Кондитер", login="cook_maria", password_hash="pass_2", role=UserRole.cook),
            User(first_name="Виктор", last_name="Быстрый", login="courier_vic", password_hash="pass_3", role=UserRole.courier),
            User(first_name="Игорь", last_name="Клиент", login="user_igor", password_hash="pass_4", role=UserRole.client, status=UserStatus.active),
            User(first_name="Анна", last_name="Новичок", login="user_anna", password_hash="pass_5", role=UserRole.client, status=UserStatus.active),
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