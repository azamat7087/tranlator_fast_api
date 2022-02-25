from fastapi import APIRouter
from translator import translator
from auth import auth

routes = APIRouter()

routes.include_router(translator.router, prefix="/translate")
routes.include_router(auth.router, prefix="/auth")
