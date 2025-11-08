from fastapi import Depends, FastAPI, HTTPException, Path
import models
from routers import authorisation, todos 
from database import SessionLocal, engine, Base

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(authorisation.router) # Include the authorization router
app.include_router(todos.router)  # Include the todos router

