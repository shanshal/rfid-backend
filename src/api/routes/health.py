from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
def ping():
    return {"status":"200 ok"}
