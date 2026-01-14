import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas
from ..auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["Projects"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ProjectResponse)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        new_project = models.Project(
            name=project.name,
            owner_id=current_user.id
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        logger.info(f"Project '{project.name}' created by user {current_user.email}")
        return new_project
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        db.rollback()
        raise

@router.get("/", response_model=list[schemas.ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    projects = db.query(models.Project).filter(
        models.Project.owner_id == current_user.id
    ).all()
    logger.debug(f"User {current_user.email} listed {len(projects)} projects")
    return projects