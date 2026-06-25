from database import engine, SessionLocal, Base
from models import User, UserRole
from auth import hash_password

# Создаем таблицы
Base.metadata.create_all(bind=engine)

db = SessionLocal()

if db.query(User).count() == 0:
    users = [
        User(
            badge_number="ADMIN-001",
            full_name="Иванов И.И. (завсклад)",
            workshop="Цех 1",
            role=UserRole.ADMIN,
            hashed_password=hash_password("admin123")
        ),
        User(
            badge_number="METRO-001",
            full_name="Петров П.П. (метролог)",
            workshop="Лаборатория",
            role=UserRole.METROLOGIST,
            hashed_password=hash_password("metro123")
        ),
        User(
            badge_number="W-5432",
            full_name="Сидоров С.С. (мастер)",
            workshop="Цех 3",
            role=UserRole.WORKER,
            hashed_password=hash_password("worker123")
        ),
    ]
    db.add_all(users)
    db.commit()
    print("Тестовые пользователи созданы!")
else:
    print("Пользователи уже есть в базе")

db.close()