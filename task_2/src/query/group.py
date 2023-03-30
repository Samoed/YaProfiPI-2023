from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.group import Group
from src.models.group import PostGroup


async def create_group(group: PostGroup, session: AsyncSession) -> int:
    group_db = Group(name=group.name, description=group.description)
    session.add(group_db)
    await session.commit()
    return group_db.id


async def query_get_groups(session: AsyncSession) -> list[Group]:
    return (await session.scalars(select(Group))).all()


async def query_get_group_by_id(group_id: int, session: AsyncSession) -> Group | None:
    return await session.scalar(select(Group).where(Group.id == group_id).options(selectinload(Group.participants)))


async def query_put_group(group_id: int, group_data: PostGroup, session: AsyncSession) -> bool:
    group = await session.get(Group, group_id)
    if group is None:
        return False
    group.name = group_data.name
    group.description = group_data.description
    await session.commit()
    return True


async def query_delete_group(group_id: int, session: AsyncSession) -> int | None:
    query = delete(Group).where(Group.id == group_id).returning(Group.id)
    deleted_group_id = await session.scalar(query)
    await session.commit()
    return deleted_group_id
