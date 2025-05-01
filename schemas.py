from pydantic import BaseModel
from typing import List, Optional, Dict

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class CourseBase(BaseModel):
    yaml_id: str
    title: str
    points: int
    creator_info: Optional[str] = None

class ModuleBase(BaseModel):
    yaml_id: str
    title: str
    points: int
    order: int

class SectionBase(BaseModel):
    yaml_id: str
    title: str
    content: str
    points: int
    order: int

class ExerciseBase(BaseModel):
    content: str
    points: int

class CourseResponse(BaseModel):
    id: int
    yaml_id: str
    title: str
    points: int
    creator_info: Dict
    modules: List[ModuleBase]

    class Config:
        orm_mode = True

class CompletionResponse(BaseModel):
    item_type: str
    item_id: int
