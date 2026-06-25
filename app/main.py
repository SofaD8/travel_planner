from fastapi import (
    FastAPI,
    Depends,
    status,
    HTTPException
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from contextlib import asynccontextmanager

from app.database import (
    Base,
    engine,
    get_db
)
from app.models import Project, Place
from app.services import TravelPlannerService
from app.schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    PlaceCreate,
    PlaceResponse,
    PlaceUpdate
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Travel Planner API", lifespan=lifespan)


@app.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_project(
        project_data: ProjectCreate,
        db: AsyncSession = Depends(get_db)
):
    return await TravelPlannerService.create_project(
        db=db,
        name=project_data.name,
        description=project_data.description,
        start_date=project_data.start_date,
        external_places=project_data.external_places
    )


@app.get("/projects", response_model=list[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).options(joinedload(Project.places)))
    return result.scalars().unique().all()


@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project)
        .filter(Project.id == project_id)
        .options(joinedload(Project.places))
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@app.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
        project_id: int,
        project_data: ProjectUpdate,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    for key, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)

    await db.commit()

    result = await db.execute(
        select(Project)
        .filter(Project.id == project_id)
        .options(joinedload(Project.places))
    )
    return result.scalars().first()


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    await TravelPlannerService.delete_project(db, project_id)
    return None


@app.post(
    "/projects/{project_id}/places",
    response_model=PlaceResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_place_to_project(
        project_id: int,
        place_data: PlaceCreate,
        db: AsyncSession = Depends(get_db)
):
    return await TravelPlannerService.add_place_to_project(
        db=db,
        project_id=project_id,
        external_id=place_data.external_id,
        notes=place_data.notes
    )


@app.get("/projects/{project_id}/places/{place_id}", response_model=PlaceResponse)
async def get_place_in_project(
        project_id: int,
        place_id: int,
        db: AsyncSession = Depends(get_db)
):
    return await TravelPlannerService.get_place_in_project(
        db=db,
        project_id=project_id,
        place_id=place_id
    )


@app.get("/projects/{project_id}/places", response_model=list[PlaceResponse])
async def list_places_for_project(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Place).filter(Place.project_id == project_id))
    return result.scalars().all()


@app.patch("/projects/{project_id}/places/{place_id}", response_model=PlaceResponse)
async def update_place(
        project_id: int,
        place_id: int,
        place_data: PlaceUpdate,
        db: AsyncSession = Depends(get_db)
):
    return await TravelPlannerService.update_place_status(
        db=db,
        project_id=project_id,
        place_id=place_id,
        is_visited=place_data.is_visited,
        notes=place_data.notes
    )
