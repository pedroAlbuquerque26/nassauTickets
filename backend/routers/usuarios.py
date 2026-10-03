from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.auth import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from services import usuarios as usuarios_service
from services.auth import require_gestor

usuarios_router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(require_gestor)],
)


@usuarios_router.get("/get", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return usuarios_service.listar(db)


@usuarios_router.post("/create", response_model=UsuarioResponse)
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return usuarios_service.criar(db, dados.model_dump())
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@usuarios_router.put("/update/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(usuario_id: int, dados: UsuarioUpdate, db: Session = Depends(get_db)):
    try:
        return usuarios_service.atualizar(db, usuario_id, dados.model_dump(exclude_unset=True))
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@usuarios_router.delete("/delete/{usuario_id}")
def remover_usuario(usuario_id: int, db: Session = Depends(get_db)):
    try:
        usuarios_service.remover(db, usuario_id)
        return {"detail": "Usuario removido com sucesso"}
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
