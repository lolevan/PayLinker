import asyncio

from app.models import Base, User
from app.utils import hash_password
from app.config import DATABASE_URL

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Создание асинхронного движка для работы с базой данных
engine = create_async_engine(DATABASE_URL, echo=True)
# Создание асинхронной сессии для взаимодействия с базой данных
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Асинхронная функция для создания начальных данных
async def create_initial_data():
    # Создание всех таблиц в базе данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создание сессии для работы с базой данных
    async with async_session() as session:
        async with session.begin():
            # Проверка существования пользователя с email 'user@example.com'
            existing_user = await session.execute(select(User).filter_by(email='user@example.com'))
            if existing_user.scalar():
                print("User with email 'user@example.com' already exists.")
            else:
                # Создание пользователя 'Test User'
                user = User(email='user@example.com', full_name='Test User', password=hash_password('password'),
                            is_admin=0)
                session.add(user)

            # Проверка существования администратора с email 'admin@example.com'
            existing_admin = await session.execute(select(User).filter_by(email='admin@example.com'))
            if existing_admin.scalar():
                print("User with email 'admin@example.com' already exists.")
            else:
                # Создание администратора 'Admin User'
                admin = User(email='admin@example.com', full_name='Admin User', password=hash_password('password'),
                             is_admin=1)
                session.add(admin)

            # Коммит изменений в базе данных
            await session.commit()

# Запуск асинхронной функции для создания начальных данных
asyncio.run(create_initial_data())
