from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Guiche
from schemas.auth import GuicheCreate, GuicheResponse, GuicheUpdate
from services import guiches as guiches_service
from services.auth import require_gestor

guiches_router = APIRouter(prefix="/guiches", tags=["Guiches"])


@guiches_router.get("/get", response_model=list[GuicheResponse])
def listar_guiches(
    incluir_inativos: bool = True,
    db: Session = Depends(get_db),
):
    return guiches_service.listar(db, incluir_inativos=incluir_inativos)


@guiches_router.post("/create", response_model=GuicheResponse)
def criar_guiche(
    dados: GuicheCreate,
    _: dict = Depends(require_gestor),
    db: Session = Depends(get_db),
):
    try:
        return guiches_service.criar(db, dados.model_dump())
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@guiches_router.put("/update/{guiche_id}", response_model=GuicheResponse)
def atualizar_guiche(
    guiche_id: int,
    dados: GuicheUpdate,
    _: dict = Depends(require_gestor),
    db: Session = Depends(get_db),
):
    try:
        return guiches_service.atualizar(db, guiche_id, dados.model_dump(exclude_unset=True))
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@guiches_router.delete("/delete/{guiche_id}")
def remover_guiche(
    guiche_id: int,
    _: dict = Depends(require_gestor),
    db: Session = Depends(get_db),
):
    try:
        guiches_service.remover(db, guiche_id)
        return {"detail": "Guiche removido com sucesso"}
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
