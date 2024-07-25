from app.models import Base, User, Account
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import hash_password

DATABASE_URL = 'postgresql+asyncpg://user:password@db/myapp'

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def create_initial_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создаем таблицы

    async with async_session() as session:
        async with session.begin():
            user = User(email='user@example.com', full_name='Test User', password=hash_password('userpass'))
            admin = User(email='admin@example.com', full_name='Admin User', password=hash_password('adminpass'),
                         is_admin=1)
            session.add(user)
            session.add(admin)
            await session.commit()

        async with session.begin():
            account = Account(user_id=user.id, balance=1000)
            session.add(account)
            await session.commit()

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_initial_data())
