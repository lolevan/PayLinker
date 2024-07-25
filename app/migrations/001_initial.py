from app.models import Base, User, Account
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

DATABASE_URL = 'postgresql+asyncpg://user:password@db/myapp'

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def create_initial_data():
    async with async_session() as session:
        async with session.begin():
            user = User(email='user@example.com', full_name='Test User', password='userpass')
            admin = User(email='admin@example.com', full_name='Admin User', password='adminpass', is_admin=1)
            session.add(user)
            session.add(admin)
            await session.commit()

            account = Account(user_id=user.id, balance=1000)
            session.add(account)
            await session.commit()

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_initial_data())
