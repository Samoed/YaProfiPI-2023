from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.database.participant import Participant


class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)
    participants: Mapped[list["Participant"]] = relationship("Participant", back_populates="group")
