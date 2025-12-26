from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/")
async def root(request: Request):
    return {"message": "Hello World"}