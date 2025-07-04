from pydantic import BaseModel

class categoryCreate(BaseModel):
    category_name : str

class categoryResponse(BaseModel):
    category_id : int
    category_name : str
