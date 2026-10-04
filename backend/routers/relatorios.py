from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.relatorios import AuditoriaResponse, DesempenhoResponse, RelatorioResponse
from services import relatorios as relatorios_service
from services.auth import require_gestor

relatorios_router = APIRouter(
    prefix="/relatorios",
    tags=["Relatorios"],
    dependencies=[Depends(require_gestor)],
)


def _parse_data(data: str = None) -> date:
    if not data:
        return date.today()
    try:
        return date.fromisoformat(data)
    except ValueError:
        raise HTTPException(status_code=400, detail="Data invalida, use o formato YYYY-MM-DD")


@relatorios_router.get("/diario", response_model=RelatorioResponse)
def diario(data: str = None, db: Session = Depends(get_db)):
    return relatorios_service.relatorio_diario(db, _parse_data(data))


@relatorios_router.get("/mensal", response_model=RelatorioResponse)
def mensal(ano: int = None, mes: int = None, db: Session = Depends(get_db)):
    hoje = date.today()
    ano = ano or hoje.year
    mes = mes or hoje.month
    if not 1 <= mes <= 12:
        raise HTTPException(status_code=400, detail="Mes invalido")
    return relatorios_service.relatorio_mensal(db, ano, mes)


@relatorios_router.get("/auditoria", response_model=AuditoriaResponse)
def auditoria(data: str = None, db: Session = Depends(get_db)):
    return relatorios_service.relatorio_auditoria(db, _parse_data(data))


@relatorios_router.get("/desempenho", response_model=DesempenhoResponse)
def desempenho(data: str = None, db: Session = Depends(get_db)):
    return relatorios_service.relatorio_desempenho(db, _parse_data(data))
