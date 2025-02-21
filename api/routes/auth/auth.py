from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
def get_profile():
    return {"message": "Authentication Route"}
