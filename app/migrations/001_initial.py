import asyncio

from app.models import Base, User
from app.utils import hash_password
from app.config import DATABASE_URL

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def create_initial_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        async with session.begin():
            existing_user = await session.execute(select(User).filter_by(email='user@example.com'))
            if existing_user.scalar():
                print("User with email 'user@example.com' already exists.")
            else:
                user = User(email='user@example.com', full_name='Test User', password=hash_password('password'),
                            is_admin=0)
                session.add(user)

            existing_admin = await session.execute(select(User).filter_by(email='admin@example.com'))
            if existing_admin.scalar():
                print("User with email 'admin@example.com' already exists.")
            else:
                admin = User(email='admin@example.com', full_name='Admin User', password=hash_password('password'),
                             is_admin=1)
                session.add(admin)

            await session.commit()


asyncio.run(create_initial_data())
