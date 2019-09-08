from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse

from typing import List

import searchlib

class Result(BaseModel):
    value: List[str] = []

class Message(BaseModel):
    message: str

app = FastAPI()

searchAPI = searchlib.SearchAPI("textsearch")

@app.get('/')
async def index():
    return JSONResponse(status_code=200, content={"message": "Server Works!"})

@app.get('/health')
async def health():
    return JSONResponse(status_code=200, content={"message": "OK"})

@app.get('/ready')
async def ready():
    if searchAPI.ready():
        return JSONResponse(status_code=200, content={"message": "OK"})
    return JSONResponse(status_code=503, content={"message": "Not ready yet"})

@app.get('/v0/search', responses={404: {"model": Message}})
async def search(q: str = None):
    if q:
        print("Searching for: ", q)
        sr = searchAPI.search(q)
        return sr
    return JSONResponse(status_code=404, content={"message": "Response not available"})


@app.get('/v0/autocomplete', responses={404: {"model": Message}})
async def autocomlete(q: str = None):
    if q:
        print("Searching for: ", q)
        sr = searchAPI.autocomlete(q)
        return sr
    return JSONResponse(status_code=404, content={"message": "Response not available"})

@app.post('/v0/insertsentence', responses={404: {"model": Message}})
async def insertSentence(id: str = None, sentence: str = None):
    if id and sentence:
        print("Insert sentence: ", sentence)
        sr = searchAPI.insertSentence(id, sentence)
        return sr
    return JSONResponse(status_code=404, content={"message": "Response not available"})

@app.post('/v0/insertparagraph', responses={404: {"model": Message}})
async def insertParagraph(id: str = None, sentence: str = None):
    if id and sentence:
        print("Insert sentence: ", sentence)
        sr = searchAPI.insertParagraph(id, sentence)
        return sr
    return JSONResponse(status_code=404, content={"message": "Response not available"})
