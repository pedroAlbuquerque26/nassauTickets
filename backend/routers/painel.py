from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.painel import PainelResponse
from services import painel as painel_service

painel_router = APIRouter(prefix="/painel", tags=["Painel"])


@painel_router.get("", response_model=PainelResponse)
@painel_router.get("/", include_in_schema=False)
def painel(db: Session = Depends(get_db)):
    return painel_service.painel(db)
