from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.database.group import Group


class Participant(Base):
    __tablename__ = "participant"

    participant_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str]
    wish: Mapped[str] = mapped_column(nullable=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("participant.participant_id"), nullable=True)
    # recipient: Mapped["Participant"] = relationship("Participant", remote_side="participant_id")
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"))
    group: Mapped["Group"] = relationship("Group", back_populates="participants")
