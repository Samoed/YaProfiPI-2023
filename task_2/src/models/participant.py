from pydantic import BaseModel


class ParticipantModel(BaseModel):
    id: int
    name: str
    wish: str | None


class ParticipantWithRecipient(ParticipantModel):
    recipient: ParticipantModel | None


class PostParticipant(BaseModel):
    name: str
    wish: str | None
