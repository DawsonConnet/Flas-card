from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import random

templates = Jinja2Templates(directory="templates")

app = FastAPI()

class Card(BaseModel):
    id:int
    question:str
    answer:str
    set_id: int
    wrong_count:int=0
    count: int=0

class User(BaseModel):
    id: int
    name: str
    email: str
    sets: List[int] = []

class Deck(BaseModel):
    id: int
    name: str
    card_ids: List[int] = []
    user_id: int   

class Set(BaseModel):
    id: int
    name: str
    user_id: int 
    card_ids: List[int] = []

app.mount("/static", StaticFiles(directory="static"), name="static")

set_list =[
    Set(id=1, name="Dawson's Questions", user_id=1, card_ids=[1])
]

user_list =[
    User(id=1, name="Dawson", email="Dawson_connet@taylor.edu", sets=[1])
    ,User(id=2, name="Joe", email="Dawsonconnet@gmail.com", sets=[1])
]

card_list = [Card(id=1, question="When is silksong?", answer="Yesterday", set_id=1)
            ,Card(id=2, question="is it fun?", answer="YES", set_id=1)
            ,Card(id=3, question="qu'est-ce que c'est?", answer="the wind", set_id=1)
            ,Card(id=4, question="Where is Taylor located?", answer="Upland, IN", set_id=1)
            ,Card(id=5, question="am i out of question ideas?", answer="yes", set_id=1)
        ]

@app.get("/", response_class=HTMLResponse)
async def root(request:Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"cards": card_list}
    )

#Query parameter
@app.get("/cards")
async def getCards(q:str=""):
    search_results = []
    for card in card_list:
        if q in card.question:
            search_results.append(card)
    return search_results

#Path Parameter
@app.get("/cards/{card_id}", name="get_card", response_class=HTMLResponse)
async def get_card_by_id(request:Request, card_id:int):
    for card in card_list:
        if card.id == card_id:
            return templates.TemplateResponse(
                request=request, name="card.html", context={"card": card}
    )
    return None

@app.get("/play", response_class=HTMLResponse)
async def play(request:Request):
    card = card_list[random.randint(0, (len(card_list)-1))]
    return templates.TemplateResponse(
        request=request, name="play.html", context={"card": card}
    )

@app.get("/sets", response_class=HTMLResponse)
async def list_sets(request: Request):
    return templates.TemplateResponse(
        name="sets.html", request=request, context={"sets": set_list}
    )

@app.get("/users", response_class=HTMLResponse)
async def list_sets(request: Request):
    return templates.TemplateResponse(
        name="users.html", request=request, context={"users": user_list}
    )

@app.post("/cards/{card_id}/wrong")
async def mark_wrong(card_id: int):
    for card in card_list:
        if card.id == card_id:
            card.wrong_count += 1
            card.count += 1
            return card
        
@app.post("/cards/{card_id}/attempt")
async def mark_attempt(card_id: int):
    for card in card_list:
        if card.id == card_id:
            card.count += 1
            return card

#Post Request to add card
@app.post("/card/add")
async def addCard(card:Card):
    card_list.append(card)
    return card_list