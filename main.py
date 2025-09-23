from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlmodel import Session, Field, SQLModel, create_engine, select, Relationship
from db.session import create_db_and_tables, SessionDep
from db.models import Card, Set, User
from routers import cards, sets, users
import random

templates = Jinja2Templates(directory="templates")

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(cards.router)
app.include_router(sets.router)
app.include_router(users.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, session: SessionDep):
    cards = session.exec(select(Card)).all()
    return templates.TemplateResponse(request, "index.html", {"cards": cards})

@app.get("/play", response_class=HTMLResponse)
async def play(request: Request, session: SessionDep):
    cards = session.exec(select(Card)).all()
    if not cards:
        raise HTTPException(status_code=404, detail="No cards available")
    
    card = random.choice(cards)
    return templates.TemplateResponse(request, "play.html", {"card": card})