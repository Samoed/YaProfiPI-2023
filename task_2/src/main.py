from typing import Annotated

import uvicorn
from alembic.command import upgrade
from alembic.config import Config
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy_utils import create_database, database_exists

from src.database.session_manager import SessionManager, get_session
from src.models.group import GetGroup
from src.query.group import query_get_groups
from src.route.group import router as group_router
from src.settings import Settings

app = FastAPI()
app.include_router(group_router)


def run_upgrade(connection: AsyncEngine, cfg: Config) -> None:
    cfg.attributes["connection"] = connection
    upgrade(cfg, "head")


@app.on_event("startup")
async def startup() -> None:
    if not database_exists(Settings().database_uri_sync):
        create_database(Settings().database_uri_sync)
    # Base.metadata.create_all(bind=engine)
    config = Config("alembic.ini")
    config.attributes["configure_logger"] = False
    engine = SessionManager().engine
    async with engine.begin() as conn:
        await conn.run_sync(run_upgrade, config)


@app.get("/groups")
async def get_groups(session: Annotated[AsyncSession, Depends(get_session)]) -> list[GetGroup]:
    db_groups = await query_get_groups(session)
    return [GetGroup(id=group.id, name=group.name, description=group.description) for group in db_groups]


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
