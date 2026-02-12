from pydantic import BaseModel

class categoryCreate(BaseModel):
    name : str

class categoryResponse(BaseModel):
    id : int
    name : str
