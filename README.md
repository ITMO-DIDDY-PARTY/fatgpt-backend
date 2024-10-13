# FatGPT REST API 

## Description

FatGPT REST API is used for generation on various recipes. Used by our mobile application.

Tools:

- Docker - for easy deployment and testing purposes
- FastAPI - Python framework for API development
- ChatGPT - OpenAI API to generate recipes from picture


## Deployment

### Using Docker (recommended)

```bash
$ docker-compose up --build -d
```

### Manually

```bash
$ pip install -r requirements.txt
$ uvicorn app:app --reload
```
