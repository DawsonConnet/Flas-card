from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form, WebSocketDisconnect, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlmodel import select
from db.session import create_db_and_tables, SessionDep
from db.models import Card, Set
from routers import cards, sets, users
import random
import json

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

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str,WebSocket] = {}
        
        
    async def connect(self, client_id: str, websocket:WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        if isinstance(message, (dict, list)):
            message = json.dumps(message)
        for connection in list(self.active_connections.values()):
            try:
                await connection.send_text(message)
            except:
                pass

async def broadcast_scores():
    await manager.broadcast({"type": "score_update", "players": [{"name": name, "score": score} for name, score in players.items()]})


manager = ConnectionManager()
current_card = None
players = {}

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

@app.get("/playwithfriends")
async def playwithfriends(request:Request, session:SessionDep, response_class=HTMLResponse):
    return templates.TemplateResponse(request, "playWithFriends.html")

@app.post("/playwithfriends")
async def enterplay(request: Request, session: SessionDep,response_class=HTMLResponse, username: str= Form(...)):
    sets = session.exec(select(Set)).all()
    response = templates.TemplateResponse(request=request, name="playWithFriends.html", context={"username": username, "sets": sets})
    response.set_cookie(key="username", value=username, httponly=False)
    return response
    
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, session: SessionDep):
    global current_card
    if client_id in players:
        pass
    else:
        players[client_id] = 0
    await manager.connect(client_id, websocket)
    await broadcast_scores()
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "new_question":
                selected_set_ids = data.get("sets", [])
                
                try:
                    selected_ids_int = [int(sid) for sid in selected_set_ids if sid.isdigit()]
                except ValueError:
                    selected_ids_int = []
                if selected_ids_int:
                    cards = session.exec(select(Card).where(Card.set_id.in_(selected_ids_int))).all()
                else:
                    cards = session.exec(select(Card)).all()

                if cards:
                    selected_card = random.choice(cards)
                    current_card = selected_card
                    card_data = {"id": selected_card.id, "question": selected_card.front}
                    await manager.broadcast({"type": "show_card", "card": card_data})

            elif msg_type == "message":
                message = data.get("payload", {}).get("message", "")
                if current_card and message.lower() == current_card.back.lower():
                    players[client_id] += 1
                    await manager.broadcast({"type": "chat","sender": "System","message": f" {client_id} correct The answer was '{current_card.back}'."})
                    await broadcast_scores()
                    cards = session.exec(select(Card)).all()
                    if cards:
                        current_card = random.choice(cards)
                        await manager.broadcast({"type": "show_card","card": {"id": current_card.id, "question": current_card.front}})
                else:
                    await manager.broadcast({"type": "chat", "sender": client_id, "message": message})
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        if client_id in players:
            del players[client_id]
        await broadcast_scores()
        await manager.broadcast({"type": "chat", "sender": "System", "message": f"{client_id} left the game."})