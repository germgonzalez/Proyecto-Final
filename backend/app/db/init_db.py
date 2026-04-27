from app.db.session import engine
from app.db.base import Base
import app.models  # noqa: F401 — registra todos los modelos con SQLAlchemy


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
