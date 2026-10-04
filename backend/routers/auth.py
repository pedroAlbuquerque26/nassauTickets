from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario
from schemas.auth import LoginRequest, LoginResponse, UsuarioResponse
from services import usuarios as usuarios_service
from services.auth import get_current_user

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", response_model=LoginResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    try:
        return usuarios_service.login(db, dados.login, dados.senha)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@auth_router.get("/me", response_model=UsuarioResponse)
def me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == current_user["id"]).first()
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuario nao encontrado")
    return usuario
