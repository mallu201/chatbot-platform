from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class ProjectCreate(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class PromptCreate(BaseModel):
    name: str
    content: str


class PromptUpdate(BaseModel):
    name: str
    content: str


class PromptResponse(BaseModel):
    id: int
    project_id: int
    name: str
    content: str

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    project_id: int
    message: str


class FileResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    openai_file_id: str
    file_size: int

    class Config:
        from_attributes = True
