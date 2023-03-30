from pydantic import BaseModel
from pydantic.fields import Field

from src.models.participant import ParticipantWithRecipient


class PostGroup(BaseModel):
    name: str = Field(description="Название группы")
    description: str | None = Field(description="Описание группы")


class GetGroup(BaseModel):
    id: int
    name: str = Field(description="Название группы")
    description: str | None = Field(description="Описание группы")


class GetGroupById(GetGroup):
    participants: list[ParticipantWithRecipient] | None
