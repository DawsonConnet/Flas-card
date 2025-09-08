from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
import random

templates = Jinja2Templates(directory="templates")

app = FastAPI()

class Card(BaseModel):
    id:int
    question:str
    answer:str

card_list = [Card(id=1, question="When is silksong?", answer="Yesterday")
            ,Card(id=2, question="is it fun?", answer="YES")
            ,Card(id=3, question="qu'est-ce que c'est?", answer="the wind")
            ,Card(id=4, question="Where is Taylor located?", answer="Upland, IN")
            ,Card(id=5, question="am i out of question ideas?", answer="yes")
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
@app.get("/cards/{card_id}")
async def getCardById(card_id:int):
    for card in card_list:
        if card.id == card_id:
            return card
    return None

@app.get("/play", response_class=HTMLResponse)
async def play(request:Request):
    card = card_list[random.randint(0, (len(card_list)-1))]
    return templates.TemplateResponse(
        request=request, name="play.html", context={"card": card}
    )

#Post Request to add card
@app.post("/card/add")
async def addCard(card:Card):
    card_list.append(card)
    return card_list