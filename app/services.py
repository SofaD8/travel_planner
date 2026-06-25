from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from datetime import date

from app.models import Project, Place
from app.clients import ArtInstituteClient


class TravelPlannerService:

    @staticmethod
    async def create_project(
            db: AsyncSession,
            name: str,
            description: str | None = None,
            start_date: date | None = None,
            external_places: list[int] | None = None
    ) -> Project:
        if not external_places:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one place is required to create a project."
            )

        if len(set(external_places)) != len(external_places):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate external place IDs are not allowed."
            )

        new_project = Project(
            name=name,
            description=description,
            start_date=start_date
        )
        db.add(new_project)
        await db.flush()

        for ext_id in external_places:
            is_valid = await ArtInstituteClient.validate_artwork(ext_id)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Place with external ID {ext_id} "
                           f"does not exist in Art Institute API."
                )

            new_place = Place(
                project_id=new_project.id,
                external_id=ext_id
            )
            db.add(new_place)

        await db.commit()
        await db.refresh(new_project)
        return new_project

    @staticmethod
    async def add_place_to_project(
            db: AsyncSession,
            project_id: int,
            external_id: int,
            notes: str | None = None
    ) -> Place:

        result = await db.execute(select(Project).filter(
            Project.id == project_id)
        )
        project = result.scalars().first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found."
            )


        places_count_result = await db.execute(select(Place).filter(
            Place.project_id == project_id)
        )
        current_places = places_count_result.scalars().all()
        if len(current_places) >= 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add more places. "
                       "Limit of 10 places per project reached."
            )


        if any(p.external_id == external_id for p in current_places):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This place is already added to the project."
            )


        is_valid = await ArtInstituteClient.validate_artwork(external_id)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Place with external ID {external_id} "
                       f"does not exist in Art Institute API."
            )

        new_place = Place(
            project_id=project_id,
            external_id=external_id,
            notes=notes
        )
        db.add(new_place)
        await db.commit()
        await db.refresh(new_place)
        return new_place

    @staticmethod
    async def get_place_in_project(
            db: AsyncSession,
            project_id: int,
            place_id: int
    ) -> Place:
        result = await db.execute(
            select(Place).filter(
                Place.id == place_id,
                Place.project_id == project_id
            )
        )
        place = result.scalars().first()
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place within this project not found."
            )
        return place

    @staticmethod
    async def delete_project(db: AsyncSession, project_id: int):
        result = await db.execute(
            select(Project)
            .filter(Project.id == project_id)
            .options(joinedload(Project.places))
        )
        project = result.scalars().first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found."
            )

        if any(place.is_visited for place in project.places):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete project because "
                       "some of its places are already marked as visited."
            )

        await db.delete(project)
        await db.commit()

    @staticmethod
    async def update_place_status(
            db: AsyncSession,
            project_id: int,
            place_id: int,
            is_visited: bool | None = None,
            notes: str | None = None
    ) -> Place:
        result = await db.execute(
            select(Place).filter(
                Place.id == place_id,
                Place.project_id == project_id
            )
        )
        place = result.scalars().first()
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place within this project not found."
            )

        if is_visited is not None:
            place.is_visited = is_visited
        if notes is not None:
            place.notes = notes

        await db.commit()
        await db.refresh(place)
        return place
