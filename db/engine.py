import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


load_dotenv()


engine = create_async_engine(url=os.environ.get("DB_URI"))
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
