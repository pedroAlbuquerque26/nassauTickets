from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services import expediente as expediente_service
from services.auth import require_gestor

expediente_router = APIRouter(prefix="/expediente", tags=["Expediente"])


@expediente_router.get("/status")
def status(db: Session = Depends(get_db)):
    return expediente_service.status_expediente(db)


@expediente_router.post("/encerrar")
def encerrar(_: dict = Depends(require_gestor), db: Session = Depends(get_db)):
    descartadas = expediente_service.encerrar_expediente(db)
    return {"detail": f"{descartadas} senha(s) descartada(s) ao encerrar o expediente"}
