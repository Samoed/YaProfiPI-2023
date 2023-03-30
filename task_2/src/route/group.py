from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session_manager import get_session
from src.models.group import GetGroupById, PostGroup
from src.models.participant import (
    ParticipantModel,
    ParticipantWithRecipient,
    PostParticipant,
)
from src.query.group import (
    create_group,
    query_delete_group,
    query_get_group_by_id,
    query_put_group,
)
from src.query.participant import (
    add_participant,
    get_participant_recipient,
    get_participants,
    query_delete_participant,
    toss_participants,
)

router = APIRouter(prefix="/group", tags=["group"])


@router.post("")
async def post_group(group: Annotated[PostGroup, Body], session: Annotated[AsyncSession, Depends(get_session)]) -> int:
    return await create_group(group, session)


@router.get("/{group_id}")
async def get_group(
    group_id: Annotated[int, Path], session: Annotated[AsyncSession, Depends(get_session)]
) -> GetGroupById:
    group = await query_get_group_by_id(group_id, session)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    participants = await get_participants(group_id, session)
    model_participants = {}
    if participants:
        model_participants = {
            key: ParticipantModel(id=val.participant_id, name=val.name, wish=val.wish)
            for key, val in participants.items()
            if val is not None
        }
    return GetGroupById(
        id=group.id,
        name=group.name,
        description=group.description,
        participants=(
            [
                ParticipantWithRecipient(
                    id=participant.participant_id,
                    name=participant.name,
                    wish=participant.wish,
                    recipient=model_participants.get(participant.recipient_id, None),
                )
                for participant in group.participants
            ]
            if group.participants is not None
            else None
        ),
    )


@router.put("/{group_id}")
async def put_group(
    group_id: Annotated[int, Path],
    group_data: Annotated[PostGroup, Body],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None | str:
    if group_data.name == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is empty")
    result = await query_put_group(group_id, group_data, session)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return jsonable_encoder("ok")


@router.delete("/{group_id}")
async def delete_group(group_id: Annotated[int, Path], session: Annotated[AsyncSession, Depends(get_session)]):
    result = await query_delete_group(group_id, session)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


@router.post("/{group_id}/participant")
async def post_participant(
    group_id: Annotated[int, Path],
    participant: Annotated[PostParticipant, Body],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> int:
    result = await add_participant(group_id, participant, session)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return result


@router.delete("/{group_id}/participant/{participant_id}")
async def delete_participant(
    group_id: Annotated[int, Path],
    participant_id: Annotated[int, Path],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    result = await query_delete_participant(group_id, participant_id, session)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


@router.post("/{group_id}/toss")
async def toss(
    group_id: Annotated[int, Path],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[ParticipantWithRecipient]:
    participants = await toss_participants(group_id, session)
    if participants is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflict")
    group = await query_get_group_by_id(group_id, session)
    if group is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflict")
    recipient = await get_participants(group_id, session)
    model_recipient = {
        key: ParticipantModel(id=val.participant_id, name=val.name, wish=val.wish)
        for key, val in recipient.items()
        if val is not None
    }
    return (
        [
            ParticipantWithRecipient(
                id=participant.participant_id,
                name=participant.name,
                wish=participant.wish,
                recipient=model_recipient.get(participant.recipient_id, None),
            )
            for participant in group.participants
        ]
        if group.participants is not None
        else None
    )


@router.get("/{group_id}/participant/{participant_id}/recipient")
async def get_recipient(
    group_id: Annotated[int, Path],
    participant_id: Annotated[int, Path],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ParticipantModel:
    recipient = await get_participant_recipient(group_id, participant_id, session)
    if recipient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return ParticipantModel(id=recipient.participant_id, name=recipient.name, wish=recipient.wish)
