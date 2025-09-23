from sqlmodel import Field, SQLModel, Relationship
from typing import List

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    sets: List["Set"] = Relationship(back_populates="user")  # keep as is

class Set(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str    
    user_id: int | None = Field(default=None, foreign_key="user.id")
    cards: List["Card"] = Relationship(back_populates="set")
    user: User | None = Relationship(back_populates="sets")

class Card(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    front: str
    back: str
    set_id: int | None = Field(default=None, foreign_key="set.id")
    set: Set | None = Relationship(back_populates="cards")
