from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, Path
from starlette import status
import models


from database import SessionLocal, engine, Base

router = APIRouter()


# Get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Sample route to read all todos  
@router.get("/", status_code=status.HTTP_200_OK)
def read_all(db: db_dependency):
    todos = db.query(models.Todos).all()
    return todos

# Get ToDo by ID including error handling and validation
@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo

# Sample route to create a new todo
@router.post("/todo", response_model=models.TodosRequest, status_code=status.HTTP_201_CREATED)
def create_todo(todo_request: models.TodosRequest, db: db_dependency):
    todo_model = models.Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()    
    db.refresh(todo_model)
    return todo_model

# Sample route to update a todo
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(todo_request: models.TodosRequest, db: db_dependency, todo_id: int = Path(gt=0)) :
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if not todo_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
    for key, value in todo_request.model_dump().items():
        setattr(todo_model, key, value)
    
    db.add(todo_model)
    db.commit()
    return


# Sample route to delete a todo
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if not todo_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
    db.delete(todo_model)
    db.commit()
    return