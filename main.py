from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlmodel import Session, Field, SQLModel, create_engine, select, Relationship
from db.session import create_db_and_tables, SessionDep
import random

templates = Jinja2Templates(directory="templates")

app = FastAPI()


#Add this
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the DB
    create_db_and_tables()
    yield

#Modify our FastAPI app
app = FastAPI(lifespan=lifespan)

class Set(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str    
    cards: list["Card"] = Relationship(back_populates="set")

class Card(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    front: str
    back: str
    set_id: int | None = Field(default=None, foreign_key="set.id")
    set: Set | None = Relationship(back_populates="cards")

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

app.mount("/static", StaticFiles(directory="static"), name="static")

set_list =[
    Set(id=1, name="Dawson's Questions", user_id=1, card_ids=[1])
]

user_list =[
    User(id=1, name="Dawson", email="Dawson_connet@taylor.edu", sets=[1])
    ,User(id=2, name="Joe", email="Dawsonconnet@gmail.com", sets=[1])
]

card_list = [Card(id=1, front="When is silksong?", back="Yesterday", set_id=1)
            ,Card(id=2, front="is it fun?", back="YES", set_id=1)
            ,Card(id=3, front="qu'est-ce que c'est?", back="the wind", set_id=1)
            ,Card(id=4, front="Where is Taylor located?", back="Upland, IN", set_id=1)
            ,Card(id=5, front="am i out of question ideas?", back="yes", set_id=1)
        ]

@app.get("/", response_class=HTMLResponse)
async def root(request:Request):
    return templates.TemplateResponse(request, "index.html", {"card": card_list})

#Query parameter
@app.get("/cards")
async def getCards(request:Request, session: SessionDep , q:str=""):
    search_results = []
    if q:
        cards = session.exec(select(Card).where(Card.front.contains(q))).all()
    else:
        cards = session.exec(select(Card)).all()
    return templates.TemplateResponse(request, "cards.html", {"cards": cards})

#Path Parameter
@app.get("/cards/{card_id}", name="get_card", response_class=HTMLResponse)
async def get_card_by_id(request: Request, card_id: int, session: SessionDep):
    db_card = session.exec(select(Card).where(Card.id == card_id)).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    return templates.TemplateResponse(request, "card.html", {"card": db_card})

@app.get("/play", response_class=HTMLResponse)
async def play(request:Request):
    card = card_list[random.randint(0, (len(card_list)-1))]
    return templates.TemplateResponse(request, "play.html", {"card": card})

@app.get("/sets", response_class=HTMLResponse)
async def list_sets(request: Request, session: SessionDep):
    sets = session.exec(select(Set).order_by(Set.name)).all()
    return templates.TemplateResponse(request, "sets.html", {"sets": sets})

@app.get("/users", response_class=HTMLResponse)
async def list_users(request: Request):
    return templates.TemplateResponse(request, "users.html", {"users": user_list})

@app.get("/sets/{set_id}", response_class=HTMLResponse)
async def get_set(request: Request, set_id: int, session: SessionDep):
    db_set = session.exec(select(Set).where(Set.id == set_id)).first()
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")
    # Changed from "sets.html" to "set.html" for individual set display
    return templates.TemplateResponse(request, "set.html", {"set": db_set})


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

@app.post("/card/add", response_class=HTMLResponse)
async def addCard(
    request: Request, 
    session: SessionDep, 
    front: str = Form(...), 
    back: str = Form(...), 
    set_id: int = Form(...)
):
    db_card = Card(front=front, back=back, set_id=set_id)
    session.add(db_card)
    session.commit()
    session.refresh(db_card)
    return templates.TemplateResponse(request, "card.html", {"card": db_card})


@app.post("/sets/add", response_class=HTMLResponse)
async def create_set(request: Request, session: SessionDep, name: str = Form(...)):
    db_set = Set(name=name)
    session.add(db_set)
    session.commit()
    session.refresh(db_set)
    return templates.TemplateResponse(request, "set.html", {"set": db_set})