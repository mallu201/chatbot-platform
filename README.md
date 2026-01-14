# Chatbot Platform

A minimal, full-stack chatbot platform built with FastAPI and OpenAI API. This platform allows users to create projects, customize AI behavior with prompts, upload files, and interact with AI agents through a chat interface.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [Contributing](#contributing)

## Features

### Core Functionality

✅ **User Authentication**
- User registration with email and password
- Secure login with JWT token-based authentication
- Password strength validation
- Email format validation

✅ **Project Management**
- Create multiple projects/agents per user
- List all user projects
- Each project is isolated per user

✅ **Prompt Management**
- Store and associate custom prompts with projects
- Create, read, update, and delete prompts
- Prompts customize AI behavior per project
- Multiple prompts per project supported

✅ **Chat Interface**
- Interactive chat with AI agents
- Project-specific chat sessions
- Uses OpenAI Responses API (gpt-4o-mini)
- Customizable system prompts per project
- Low-latency responses with retry logic

✅ **File Upload (Optional)**
- Upload files to projects using OpenAI Files API
- List and manage uploaded files
- Delete files from projects
- Files stored in OpenAI's file system

### Non-Functional Features

✅ **Security**
- Password hashing with pbkdf2_sha256
- JWT token authentication
- CORS middleware configured
- Rate limiting protection
- Environment variable-based secrets

✅ **Reliability**
- Comprehensive error handling
- Database transaction rollback on errors
- Retry logic for external API calls
- Health check endpoint
- Detailed logging system

✅ **Performance**
- Optimized database queries
- Efficient API response handling
- Request timing and monitoring

## Technology Stack

### Backend
- **FastAPI** (0.128.0) - Modern Python web framework
- **SQLAlchemy** (2.0.45) - ORM for database operations
- **SQLite** - Lightweight database
- **python-jose** (3.5.0) - JWT token handling
- **passlib** (1.7.4) - Password hashing
- **OpenAI** (2.15.0) - OpenAI API client
- **slowapi** (0.1.9) - Rate limiting
- **python-dotenv** (1.2.1) - Environment variable management
- **Uvicorn** (0.40.0) - ASGI server

### Frontend
- **HTML5** - Structure
- **JavaScript (Vanilla)** - Client-side logic
- **Jinja2 Templates** - Server-side templating

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.8+** - Check with `python --version`
2. **pip** - Python package manager
3. **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
4. **Git** (optional) - For cloning the repository

## Installation

### Step 1: Clone or Download the Repository

```bash
# If using Git
git clone <repository-url>
cd chatbot-platform

# Or download and extract the project folder
```

### Step 2: Navigate to Backend Directory

```bash
cd backend
```

### Step 3: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- FastAPI and related dependencies
- SQLAlchemy for database
- OpenAI client
- Authentication libraries
- And more...

### Step 5: Create Environment File

Create a `.env` file in the `backend` directory:

```bash
# Windows
cd backend
type nul > .env

# Linux/Mac
cd backend
touch .env
```

### Step 6: Configure Environment Variables

Open `backend/.env` and add the following:

```env
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
SECRET_KEY=your-secret-key-change-this-in-production
```

**Important Notes:**
- Replace `sk-proj-your-actual-api-key-here` with your actual OpenAI API key
- Replace `your-secret-key-change-this-in-production` with a strong random string (at least 32 characters)
- Do NOT commit the `.env` file to version control
- No quotes needed around values
- No spaces around the `=` sign

**Example:**
```env
OPENAI_API_KEY=your-'actual-api-key-here'
```

## Running the Application

### Step 1: Activate Virtual Environment

**Windows:**
```bash
cd backend
venv\Scripts\activate
```

**Linux/Mac:**
```bash
cd backend
source venv/bin/activate
```

### Step 2: Start the Server

```bash
# From the backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Alternative command:**
```bash
python -m uvicorn app.main:app --reload
```

### Step 3: Access the Application

Open your web browser and navigate to:

```
http://localhost:8000
```

You should see the login/registration page.

### Step 4: Verify Installation

1. **Check Health Endpoint:**
   ```
   http://localhost:8000/health
   ```
   Should return: `{"status": "healthy", "database": "connected"}`

2. **Check API Documentation:**
   ```
   http://localhost:8000/docs
   ```
   FastAPI automatically generates interactive API documentation.

## Usage Guide

### 1. User Registration

1. Navigate to `http://localhost:8000`
2. Click "Register here" link
3. Enter your email and password
4. Password requirements:
   - Minimum 8 characters
   - At least one letter
   - At least one number
5. Click "Register"
6. After successful registration, you'll be redirected to login

### 2. User Login

1. Enter your registered email and password
2. Click "Login"
3. Upon successful login, you'll be redirected to the dashboard
4. Your authentication token is stored in browser localStorage

### 3. Create a Project

1. From the dashboard, enter a project name
2. Click "Create Project"
3. Your project will appear in the projects list
4. You can create multiple projects

### 4. Manage Prompts

1. Select a project from the "Manage Prompts" dropdown
2. Enter a prompt name (e.g., "System Instructions")
3. Enter the prompt content (instructions for the AI)
4. Click "Create Prompt"
5. Prompts will appear below
6. You can delete prompts by clicking the "Delete" button

**Example Prompt:**
```
Name: Customer Support Bot
Content: You are a helpful customer support assistant. Always be polite, professional, and solution-oriented. Provide clear step-by-step instructions.
```

### 5. Upload Files (Optional)

1. Select a project from the "Project Files" dropdown
2. Click "Choose File" and select a file
3. Click "Upload File"
4. Files will appear in the list below
5. You can delete files by clicking "Delete"

**Note:** Files are uploaded to OpenAI's file system and can be used with assistants.

### 6. Chat with AI

1. Navigate to the Chat page (link in dashboard)
2. Select a project from the dropdown
3. Type your message in the input field
4. Click "Send"
5. The AI response will appear below
6. Continue the conversation

**Note:** The AI uses the prompts associated with the selected project. If no prompts are set, it uses a default system prompt.

## API Documentation

### Authentication Endpoints

#### Register User
```
POST /users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

#### Login
```
POST /users/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Project Endpoints

#### Create Project
```
POST /projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Project"
}
```

#### List Projects
```
GET /projects
Authorization: Bearer <token>
```

### Prompt Endpoints

#### Create Prompt
```
POST /projects/{project_id}/prompts
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "System Instructions",
  "content": "You are a helpful assistant..."
}
```

#### List Prompts
```
GET /projects/{project_id}/prompts
Authorization: Bearer <token>
```

#### Update Prompt
```
PUT /projects/prompts/{prompt_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "content": "Updated content..."
}
```

#### Delete Prompt
```
DELETE /projects/prompts/{prompt_id}
Authorization: Bearer <token>
```

### Chat Endpoint

#### Send Message
```
POST /chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": 1,
  "message": "Hello, how are you?"
}

Response:
{
  "reply": "Hello! I'm doing well, thank you for asking..."
}
```

### File Endpoints

#### Upload File
```
POST /projects/{project_id}/files
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <file>
```

#### List Files
```
GET /projects/{project_id}/files
Authorization: Bearer <token>
```

#### Delete File
```
DELETE /projects/files/{file_id}
Authorization: Bearer <token>
```

### Health Check

#### Check Application Health
```
GET /health

Response:
{
  "status": "healthy",
  "database": "connected"
}
```

## Project Structure

```
chatbot-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── database.py          # Database configuration
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # Authentication logic
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── user.py          # User registration/login
│   │       ├── project.py       # Project CRUD
│   │       ├── prompt.py        # Prompt CRUD
│   │       ├── chat.py          # Chat endpoint
│   │       └── files.py         # File upload/management
│   ├── templates/               # HTML templates
│   │   ├── index.html          # Login/Registration page
│   │   ├── dashboard.html      # Project management
│   │   └── chat.html           # Chat interface
│   ├── static/
│   │   └── script.js           # Frontend JavaScript
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (create this)
│   └── app.db                  # SQLite database (auto-created)
├── README.md                   # This file
└── ARCHITECTURE_EXPLANATION.md # Architecture documentation
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not found"

**Solution:**
1. Ensure `.env` file exists in `backend/` directory
2. Check that the file contains: `OPENAI_API_KEY=sk-proj-...`
3. No quotes, no spaces around `=`
4. Restart the server after creating/modifying `.env`

### Issue: "Invalid OpenAI API key"

**Solution:**
1. Verify your API key is correct and complete
2. Check for any extra spaces or characters
3. Ensure the key starts with `sk-proj-` or `sk-`
4. Regenerate the key from OpenAI dashboard if needed
5. Clear any system environment variables: `$env:OPENAI_API_KEY = $null` (PowerShell)

### Issue: "Database locked" or SQLite errors

**Solution:**
1. Close any other processes accessing `app.db`
2. Delete `app.db` and restart (database will be recreated)
3. Ensure you're not running multiple server instances

### Issue: "Module not found" errors

**Solution:**
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check you're in the correct directory

### Issue: Port 8000 already in use

**Solution:**
1. Use a different port: `uvicorn app.main:app --reload --port 8001`
2. Or stop the process using port 8000

### Issue: CORS errors in browser

**Solution:**
1. CORS is configured to allow all origins (`allow_origins=["*"]`)
2. If issues persist, check browser console for specific errors
3. Ensure you're accessing via `http://localhost:8000` (not `file://`)

### Issue: Chat not responding or slow

**Solution:**
1. Check OpenAI API status
2. Verify API key has sufficient quota
3. Check `app.log` for error messages
4. Ensure internet connection is stable

### Issue: Password validation fails

**Solution:**
Password must meet these requirements:
- Minimum 8 characters
- At least one letter (a-z or A-Z)
- At least one number (0-9)

### Issue: "401 Unauthorized" errors

**Solution:**
1. Token may have expired (tokens expire after 60 minutes)
2. Log out and log in again to get a new token
3. Check that `Authorization: Bearer <token>` header is included

## Security Notes

### Production Deployment

⚠️ **Important:** This is a minimal implementation. For production:

1. **Change SECRET_KEY:**
   - Use a strong, random secret key (at least 32 characters)
   - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

2. **Database:**
   - Consider migrating from SQLite to PostgreSQL for better concurrency
   - Implement database backups

3. **CORS:**
   - Replace `allow_origins=["*"]` with specific allowed origins
   - Example: `allow_origins=["https://yourdomain.com"]`

4. **Rate Limiting:**
   - Current rate limiting is basic
   - Consider implementing per-user rate limits
   - Add rate limiting to specific endpoints

5. **HTTPS:**
   - Always use HTTPS in production
   - Configure SSL/TLS certificates

6. **Environment Variables:**
   - Never commit `.env` file
   - Use secure secret management (e.g., AWS Secrets Manager)

7. **Password Policy:**
   - Consider adding more password requirements
   - Implement password reset functionality
   - Add account lockout after failed attempts

8. **Logging:**
   - Don't log sensitive information (passwords, tokens)
   - Implement log rotation
   - Use structured logging

9. **API Key Security:**
   - Rotate API keys regularly
   - Monitor API usage and costs
   - Set usage limits in OpenAI dashboard

## Contributing

This is a minimal implementation for educational purposes. To extend:

1. Add user profile management
2. Implement project deletion
3. Add conversation history
4. Implement file usage in chat context
5. Add analytics and monitoring
6. Implement multi-user collaboration
7. Add export/import functionality
8. Implement search functionality

## License

This project is provided as-is for educational purposes.

## Support

For issues related to:
- **OpenAI API:** Check [OpenAI Documentation](https://platform.openai.com/docs)
- **FastAPI:** Check [FastAPI Documentation](https://fastapi.tiangolo.com/)
- **Project Issues:** Check the troubleshooting section above

## Acknowledgments

- Built with FastAPI
- Powered by OpenAI API
- Uses SQLAlchemy for database operations

---

**Last Updated:** 2024
**Version:** 1.0.0
