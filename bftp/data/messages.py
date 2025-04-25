from datetime import datetime
from pydantic import BaseModel


class Message(BaseModel):
    message: str
    timestamp: str = str(datetime.now())


class Status(BaseModel):
    message: str
