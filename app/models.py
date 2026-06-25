from typing import List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)

    places: List["Place"] = relationship(
        "Place",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    @property
    def is_completed(self) -> bool:
        if not self.places:
            return False
        return all(place.is_visited for place in self.places)


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    external_id = Column(Integer, nullable=False, index=True)
    notes = Column(String, nullable=True)
    is_visited = Column(Boolean, default=False, nullable=False)

    project = relationship("Project", back_populates="places")

    __table_args__ = (
        UniqueConstraint('project_id', 'external_id', name='_project_external_uc'),
    )
