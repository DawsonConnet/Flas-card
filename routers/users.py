from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlmodel import select
from db.session import get_session, SessionDep
from db.models import Card, Set
from fastapi.templating import Jinja2Templates
from db.models import User
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(prefix="/users")
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def list_users(request: Request, session: SessionDep):
    users = session.exec(select(User)).all()
    return templates.TemplateResponse(request,"users/users.html",{"users": users})