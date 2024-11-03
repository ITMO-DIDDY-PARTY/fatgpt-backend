from contextlib import asynccontextmanager
import secrets
from enum import Enum
import sqlite3
from typing import Annotated

from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from fastapi import FastAPI, File, HTTPException, APIRouter, Response, Depends, status

from database import User, create_db_and_tables, engine
from main import generate_recipe_from_img


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_db_and_tables()
    except Exception as e:
        print('Some error with DB: ', e)
    yield


app = FastAPI(
    title='FatGPT REST API', 
    version='0.0.1sigmaalphabeta777',
    description='API для генерации рецептов',
    contact={'name': 'ITMO DIDDY PARTY', 'url': 'https://github.com/ITMO-DIDDY-PARTY'},
    lifespan=lifespan,
)

header_scheme = APIKeyHeader(name="x-api-key", auto_error=False)

def api_key_auth(x_api_key: str = Depends(header_scheme)):
    if x_api_key != 'SECRET_KEY':
        raise HTTPException(status_code=403, detail='Invalid API key')


class RecipeType(str, Enum):
    breakfast = 'breakfast'
    lunch = 'lunch'
    dinner = 'dinner'
    low_fat = 'low_fat'
    high_protein = 'high_protein'


class RecipeResponse(BaseModel):
    markdown: str


@app.post('/generate', response_model=RecipeResponse, status_code=200, dependencies=[Depends(api_key_auth)])
async def generate_recipe(response: Response, file: Annotated[bytes, File()], type: RecipeType = None):
    """Сгенерировать рецепт по фото и выбранному типу блюда."""
    try:
        rec_md = generate_recipe_from_img(file, type)
        return RecipeResponse(markdown=rec_md)  # type: ignore
    except Exception as e:
        response.status_code = 500
        error = """# Ошибка при получении ответа от сервера. Пожалуйста, повторите позже."""
        return RecipeResponse(markdown=error)


def get_session():
    with Session(engine) as session:
        yield session


@app.post("/register")
def register(username: str, password: str, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.username == username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Create new user
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created", "user_id": user.id}


@app.post("/login")
def login(username: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or user.password != password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Generate token
    token = secrets.token_hex(16)
    user.token = token
    session.add(user)
    session.commit()
    return {"token": token}


@app.get("/users/me")
def read_users_me(token: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.token == token)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"username": user.username}
