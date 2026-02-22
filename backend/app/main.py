import logging
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .database import Base, engine
from .routes import user, project, prompt, chat, files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

# Validate OpenAI API key on startup
def validate_openai_key():
    """Validate OpenAI API key is present and properly formatted"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key and env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and line.startswith("OPENAI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
        except Exception as e:
            logger.warning(f"Could not read .env file: {e}")
    
    if not api_key:
        logger.error("⚠️  WARNING: OPENAI_API_KEY not found in .env file!")
        logger.error("   Please create backend/.env with: OPENAI_API_KEY=sk-proj-...")
        return False
    
    api_key = api_key.strip()
    if not api_key.startswith("sk-"):
        logger.error(f"⚠️  WARNING: Invalid API key format! Key should start with 'sk-'")
        return False
    
    logger.info(f"✅ OpenAI API key loaded successfully (length: {len(api_key)})")
    return True

app = FastAPI(title="Chatbot Platform", version="1.0.0")

# Validate required environment variables on startup
def validate_required_env_vars():
    """Validate all required environment variables are present"""
    errors = []
    
    # Validate OpenAI API key
    if not validate_openai_key():
        errors.append("OPENAI_API_KEY")
    
    # Validate SECRET_KEY
    try:
        from .auth import SECRET_KEY
        logger.info(f"✅ SECRET_KEY loaded successfully (length: {len(SECRET_KEY)})")
    except ValueError as e:
        logger.error(f"⚠️  WARNING: SECRET_KEY validation failed: {e}")
        errors.append("SECRET_KEY")
    
    if errors:
        logger.error(f"⚠️  Missing required environment variables: {', '.join(errors)}")
        logger.error("   The application may not work correctly. Please check backend/.env file.")
    else:
        logger.info("✅ All required environment variables are configured")

validate_required_env_vars()

# Rate limiting (basic protection against abuse)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(user.router)
app.include_router(project.router)
app.include_router(prompt.router)
app.include_router(chat.router)
app.include_router(files.router)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/chat")
def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        from .database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}
    
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Chatbot Platform", version="1.0.0")

# 👇 Add this line
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    