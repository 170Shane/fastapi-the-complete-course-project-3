from datetime import datetime
from pydantic import BaseModel, Field
from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime

class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    completed = Column(Boolean, default=False)
    created_by = Column(String)
    created_date = Column(DateTime)

class TodosRequest(BaseModel):  

    title: str = Field(min_length=3, example="Buy groceries")
    description: str = Field(min_length=3, max_length=100, example="Milk, Bread, Eggs")
    priority: int = Field(gt=0, lt=6, example=1)
    completed: bool = Field(default=False, example=False)
    created_by: str = Field(min_length=3, max_length=100, example="user@example.com")
    created_date: datetime = Field(default_factory=datetime.now, example="2023-10-05T14:48:00.000Z")


# class Todos_Response(BaseModel):
#     id: int
#     title: str
#     description: str
#     priority: int
#     completed: bool
#     created_by: str
#     created_date: datetime

#     class Config:
#         orm_mode = True