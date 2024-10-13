from enum import Enum
from typing import Annotated

from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from fastapi import FastAPI, File, HTTPException, Header, Response, Depends

from main import generate_recipe_from_img


app = FastAPI(
    title='FatGPT REST API', 
    version='0.0.1sigmaalphabeta777',
    description='API для генерации рецептов',
    contact={'name': 'ITMO DIDDY PARTY', 'url': 'https://github.com/ITMO-DIDDY-PARTY'},
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
        return RecipeResponse(markdown=rec_md)
    except Exception as e:
        response.status_code = 500
        error = """# Ошибка при получении ответа от сервера. Пожалуйста, повторите позже."""
        return RecipeResponse(markdown=error)
