import logging
import time
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from openai import OpenAI
from dotenv import load_dotenv
from slowapi.util import get_remote_address
import os
from pathlib import Path

from ..database import get_db
from ..models import Project
from ..schemas import ChatRequest
from ..auth import get_current_user

logger = logging.getLogger(__name__)

# Load .env from backend directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

router = APIRouter(prefix="/chat", tags=["Chat"])

# Get API key - check multiple sources with robust parsing
def get_api_key():
    """Get OpenAI API key from environment or .env file"""
    # First try environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key.strip()
    
    # If not found, read from .env file directly
    if env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and line.startswith("OPENAI_API_KEY="):
                        key_value = line.split("=", 1)[1]
                        # Remove quotes if present
                        key_value = key_value.strip().strip('"').strip("'")
                        if key_value:
                            return key_value
        except Exception as e:
            logger.error(f"Error reading .env file: {e}")
    
    return None

api_key = get_api_key()

if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check backend/.env file has: OPENAI_API_KEY=sk-proj-...")

# Validate key format
if not api_key.startswith("sk-"):
    raise ValueError(f"Invalid API key format. Key should start with 'sk-'. Got: {api_key[:10]}...")

# Strip any remaining whitespace
api_key = api_key.strip()

logger.info(f"OpenAI API key loaded successfully (length: {len(api_key)})")

client = OpenAI(api_key=api_key)


def call_openai_with_retry(client, model, messages, max_retries=3, delay=1):
    """Call OpenAI API with retry logic"""
    for attempt in range(max_retries):
        try:
            response = client.responses.create(
                model=model,
                input=messages,
                temperature=0.7,
                max_output_tokens=2000
            )
            return response
        except Exception as e:
            error_msg = str(e)
            # Don't retry on authentication errors
            if "401" in error_msg or "api_key" in error_msg.lower():
                raise e
            # Don't retry on quota errors
            if "quota" in error_msg.lower() or "billing" in error_msg.lower():
                raise e
            
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"OpenAI API call failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e
    return None


@router.post("")
def chat_endpoint(
    request: Request,
    data: ChatRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    logger.info(f"Chat request from user {user.email} for project {data.project_id}")
    
    project = db.query(Project).filter(
        Project.id == data.project_id,
        Project.owner_id == user.id
    ).first()

    if not project:
        logger.warning(f"Project {data.project_id} not found for user {user.email}")
        raise HTTPException(status_code=404, detail="Project not found")

    # Build system prompt from project prompts
    prompt_context = "\n".join(
        [p.content for p in project.prompts]
    ) if project.prompts else ""
    
    # Enhanced default system prompt for ChatGPT-like quality responses
    if not prompt_context:
        prompt_context = """You are ChatGPT, a large language model trained by OpenAI. 
You are helpful, harmless, and honest. You provide detailed, accurate, and well-structured responses.
When answering questions:
- Be thorough and comprehensive
- Break down complex topics into clear explanations
- Use examples when helpful
- Think step-by-step for complex problems
- Admit when you don't know something
- Format responses clearly with proper paragraphs
- Be conversational but professional
- Provide actionable advice when applicable"""

    messages = [
        {
            "role": "system",
            "content": prompt_context
        },
        {
            "role": "user",
            "content": data.message
        }
    ]

    try:
        start_time = time.time()
        response = call_openai_with_retry(client, "gpt-4o-mini", messages)
        elapsed_time = time.time() - start_time
        
        reply = response.output_text
        if not reply:
            reply = "I received your message but couldn't generate a response."
        
        logger.info(f"Chat response generated in {elapsed_time:.2f}s for user {user.email}")
        return {"reply": reply}

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Chat error for user {user.email}: {error_msg}")
        
        if "401" in error_msg or "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            raise HTTPException(
                status_code=500,
                detail="Invalid OpenAI API key. Please check your .env file and restart the server."
            )
        elif "429" in error_msg or "rate limit" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="API rate limit exceeded. Please try again later."
            )
        elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
            raise HTTPException(
                status_code=500,
                detail="OpenAI API quota exceeded. Please check your billing."
            )
        else:
            error_detail = error_msg[:150] if len(error_msg) > 150 else error_msg
            raise HTTPException(
                status_code=500,
                detail=f"AI response failed: {error_detail}"
            )
