from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.participant import Participant
from src.models.participant import PostParticipant


async def add_participant(group_id: int, participant: PostParticipant, session: AsyncSession) -> int | None:
    participant_db = Participant(
        name=participant.name,
        wish=participant.wish,
        group_id=group_id,
    )
    session.add(participant_db)
    try:
        await session.commit()
    except IntegrityError as e:
        print(e)
        return None
    return participant_db.participant_id


async def query_delete_participant(group_id: int, participant_id: int, session: AsyncSession) -> None | int:
    query = (
        delete(Participant)
        .where(Participant.participant_id == participant_id, Participant.group_id == group_id)
        .returning(Participant.participant_id)
    )
    result = await session.scalar(query)
    await session.commit()
    return result


async def get_participant_recipient(group_id: int, participant_id: int, session: AsyncSession) -> Participant | None:
    main_participant_id = (
        select(Participant.recipient_id)
        .where(Participant.participant_id == participant_id, Participant.group_id == group_id)
        .subquery()
    )
    query = select(Participant).where(Participant.participant_id == main_participant_id)
    return await session.scalar(query)


async def toss_participants(group_id: int, session: AsyncSession) -> list[Participant] | None:
    count_query = select(func.count(Participant.participant_id)).where(Participant.group_id == group_id)
    group_members_count = await session.scalar(count_query)
    if group_members_count < 4:
        return None
    participant_ids_query = select(Participant.participant_id).where(Participant.group_id == group_id)
    group_members_ids = (await session.scalars(participant_ids_query)).all()
    recipients_ids = [group_members_ids[-1], *group_members_ids[:-1]]
    for member_id, recipient_id in zip(group_members_ids, recipients_ids):
        update_query = (
            update(Participant)
            .where(Participant.group_id == group_id, Participant.participant_id == member_id)
            .values(recipient_id=recipient_id)
        )
        await session.execute(update_query)
    await session.commit()
    return (await session.execute(select(Participant))).all()


async def get_participants(group_id: int, session: AsyncSession) -> dict[int, Participant] | None:
    query = select(Participant).where(Participant.group_id == group_id)
    participants = (await session.scalars(query)).all()
    if len(participants) == 0:
        return None
    return {participant.participant_id: participant for participant in participants}
