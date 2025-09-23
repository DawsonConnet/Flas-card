from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlmodel import select
from db.session import get_session, SessionDep
from db.models import Card, Set
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(prefix="/sets")
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def list_sets(request: Request, session: SessionDep):
    sets = session.exec(select(Set).order_by(Set.name)).all()
    return templates.TemplateResponse(request, "sets/sets.html", {"sets": sets})

@router.get("/add", response_class=HTMLResponse)
async def add_set_form(request: Request):
    return templates.TemplateResponse("sets/add.html", {"request": request})

@router.post("/add")
async def add_set(
    session: SessionDep,
    name: str = Form(...)
):
    db_set = Set(name=name)
    session.add(db_set)
    session.commit()
    session.refresh(db_set)
    return RedirectResponse(url="/sets", status_code=303)

@router.get("/{set_id}", response_class=HTMLResponse)
async def get_set(request: Request, set_id: int, session: SessionDep):
    db_set = session.exec(select(Set).where(Set.id == set_id)).first()
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")
    return templates.TemplateResponse(request, "sets/set.html", {"set": db_set})

@router.get("/{set_id}/edit", response_class=HTMLResponse)
def edit_set(request: Request, session:SessionDep, set_id:int):
    db_set = session.exec(select(Set).where(Set.id==set_id)).first()
    return templates.TemplateResponse(
    "sets/add.html",
    {"request": request, "set": db_set}
  )

@router.post("/{set_id}/edit")
async def edit_set_post(
    session: SessionDep,
    set_id: int,
    name: str = Form(...)
):
    db_set = session.exec(select(Set).where(Set.id == set_id)).first()
    db_set.name = name
    session.add(db_set)
    session.commit()
    session.refresh(db_set)
    return RedirectResponse(url="/sets", status_code=303)

@router.post("/{set_id}/delete")
async def delete_set(set_id: int, session: SessionDep):
    db_set = session.exec(select(Set).where(Set.id == set_id)).first()
    cards = session.exec(select(Card).where(Card.set_id == set_id)).all()
    for card in cards:
        session.delete(card)
    session.delete(db_set)
    session.commit()
    return RedirectResponse(url="/sets", status_code=303)