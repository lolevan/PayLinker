from sanic import Sanic
from sanic_ext import Extend

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL
from app.models import Base

app = Sanic(__name__)
Extend(app)

# Database setup
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@app.listeners('before_server_start')
async def setup_db(app, loop):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.dp = async_session


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

