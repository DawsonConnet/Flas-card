from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlmodel import select
from db.session import get_session, SessionDep
from db.models import Card, Set
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

#This prefix tell this router to handle everything going to "/cards/*"
router = APIRouter(prefix="/cards")
templates = Jinja2Templates(directory="templates")

@router.get("/add", response_class=HTMLResponse)
async def show_add_card_form(request: Request, session: SessionDep):
    sets = session.exec(select(Set)).all()
    return templates.TemplateResponse(request, "cards/add.html", {"sets": sets})

@router.post("/add", response_class=HTMLResponse)
async def create_card(
    session: SessionDep,
    front: str = Form(...),
    back: str = Form(...),
    set_id: int = Form(...)
):
    card = Card(front=front, back=back, set_id=set_id)
    session.add(card)
    session.commit()
    session.refresh(card)
    return RedirectResponse(url=f"/cards/{card.id}", status_code=302)

@router.get("/")
async def getCards(request:Request, session: SessionDep , q:str=""):
    search_results = []
    if q:
        cards = session.exec(select(Card).where(Card.front.contains(q))).all()
    else:
        cards = session.exec(select(Card)).all()
    sets = session.exec(select(Set)).all()
    return templates.TemplateResponse(request, "cards/cards.html", {"cards": cards, "sets": sets})

@router.get("/{card_id}", name="get_card", response_class=HTMLResponse)
async def get_card_by_id(request: Request, card_id: int, session: SessionDep):
    db_card = session.exec(select(Card).where(Card.id == card_id)).first()
    return templates.TemplateResponse(request, "cards/card.html", {"card": db_card})

@router.post("/{card_id}/wrong")
async def mark_wrong(card_id: int, session: SessionDep):
    db_card = session.exec(select(Card).where(Card.id == card_id)).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    db_card.wrong_count += 1
    db_card.count += 1
    session.add(db_card)   
    session.commit()       
    session.refresh(db_card)  
    return db_card
        
@router.post("/{card_id}/attempt")
async def mark_attempt(card_id: int, session: SessionDep):
    db_card = session.exec(select(Card).where(Card.id == card_id)).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    db_card.count += 1
    session.add(db_card)
    session.commit()
    session.refresh(db_card)
    return db_card
    
@router.get("/{card_id}/edit")
def edit_card(request: Request, session:SessionDep, card_id:int):
    card = session.exec(select(Card).where(Card.id==card_id)).first()
    sets = session.exec(select(Set)).all()
    return templates.TemplateResponse(
    request=request, name="/cards/add.html", context={"card":card, "sets":sets}
  )

@router.post("/{card_id}/edit")
async def edit_card_post(
    session: SessionDep,
    card_id: int,
    front: str = Form(...),
    back: str = Form(...),
    set_id: int = Form(...)
):
    db_card = session.exec(select(Card).where(Card.id == card_id)).first()
    db_card.front = front
    db_card.back = back
    db_card.set_id = set_id
    session.add(db_card)
    session.commit()
    session.refresh(db_card)   
    return RedirectResponse(url=f"/cards/{db_card.id}", status_code=303)

@router.post("/{card_id}/delete")
async def delete_card(card_id: int, session: SessionDep):
    db_card = session.exec(select(Card).where(Card.id == card_id)).first()
    session.delete(db_card)
    session.commit()
    return RedirectResponse(url="/cards", status_code=303)