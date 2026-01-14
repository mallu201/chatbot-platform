import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path

from ..database import get_db
from ..models import Project, ProjectFile
from ..schemas import FileResponse
from ..auth import get_current_user

logger = logging.getLogger(__name__)

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

router = APIRouter(prefix="/projects", tags=["Files"])

def get_api_key():
    """Get OpenAI API key from environment or .env file"""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key.strip()
    
    if env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and line.startswith("OPENAI_API_KEY="):
                        key_value = line.split("=", 1)[1]
                        key_value = key_value.strip().strip('"').strip("'")
                        if key_value:
                            return key_value
        except Exception as e:
            logger.error(f"Error reading .env file: {e}")
    
    return None

api_key = get_api_key()

if not api_key:
    raise ValueError("OPENAI_API_KEY not found")

if not api_key.startswith("sk-"):
    raise ValueError(f"Invalid API key format. Key should start with 'sk-'")

api_key = api_key.strip()

logger.info(f"OpenAI API key loaded successfully for files (length: {len(api_key)})")

client = OpenAI(api_key=api_key)


@router.post("/{project_id}/files", response_model=FileResponse)
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()

    if not project:
        logger.warning(f"Project {project_id} not found for file upload")
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        contents = await file.read()
        file_size = len(contents)
        
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")

        uploaded_file = client.files.create(
            file=contents,
            purpose="assistants"
        )

        db_file = ProjectFile(
            project_id=project_id,
            filename=file.filename,
            openai_file_id=uploaded_file.id,
            file_size=file_size
        )

        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        logger.info(f"File '{file.filename}' uploaded for project {project_id}")

        return db_file

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/{project_id}/files", response_model=list[FileResponse])
def list_files(
    project_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return db.query(ProjectFile).filter(
        ProjectFile.project_id == project_id
    ).all()


@router.delete("/files/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    db_file = db.query(ProjectFile).join(Project).filter(
        ProjectFile.id == file_id,
        Project.owner_id == user.id
    ).first()

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        client.files.delete(db_file.openai_file_id)
    except:
        pass

    db.delete(db_file)
    db.commit()

    return {"message": "File deleted"}
