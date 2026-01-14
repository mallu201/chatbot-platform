import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Project, Prompt
from ..schemas import PromptCreate, PromptUpdate, PromptResponse
from ..auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["Prompts"])

# CREATE PROMPT
@router.post("/{project_id}/prompts", response_model=PromptResponse)
def create_prompt(
    project_id: int,
    data: PromptCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()

    if not project:
        logger.warning(f"Project {project_id} not found for prompt creation")
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        prompt = Prompt(
            project_id=project_id,
            name=data.name,
            content=data.content
        )

        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        logger.info(f"Prompt '{data.name}' created for project {project_id}")
        return prompt
    except Exception as e:
        logger.error(f"Error creating prompt: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create prompt")


# LIST PROMPTS
@router.get("/{project_id}/prompts", response_model=list[PromptResponse])
def list_prompts(
    project_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return db.query(Prompt).join(Project).filter(
        Prompt.project_id == project_id,
        Project.owner_id == user.id
    ).all()


# UPDATE PROMPT
@router.put("/prompts/{prompt_id}", response_model=PromptResponse)
def update_prompt(
    prompt_id: int,
    data: PromptUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    prompt = db.query(Prompt).join(Project).filter(
        Prompt.id == prompt_id,
        Project.owner_id == user.id
    ).first()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    prompt.name = data.name
    prompt.content = data.content

    db.commit()
    db.refresh(prompt)
    return prompt


# DELETE PROMPT
@router.delete("/prompts/{prompt_id}")
def delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    prompt = db.query(Prompt).join(Project).filter(
        Prompt.id == prompt_id,
        Project.owner_id == user.id
    ).first()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    db.delete(prompt)
    db.commit()
    return {"message": "Prompt deleted"}
