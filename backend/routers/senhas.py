from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.senha import EmitirRequest, FilaResponse, SenhaResponse
from services import senhas as senhas_service

senhas_router = APIRouter(prefix="/senhas", tags=["Senhas"])


@senhas_router.post("/emissir", response_model=SenhaResponse)
def emitir_senha(dados: EmitirRequest, db: Session = Depends(get_db)):
    try:
        senha = senhas_service.emitir_senha(db, dados.tipo)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    except RuntimeError as erro:
        raise HTTPException(status_code=503, detail=str(erro))
    return senhas_service.to_response(senha)


@senhas_router.get("/fila", response_model=FilaResponse)
def fila(db: Session = Depends(get_db)):
    senhas = senhas_service.listar_fila(db)
    por_tipo = {tipo: 0 for tipo in ("SP", "SG", "SE")}
    for senha in senhas:
        por_tipo[senha.tipo] += 1
    return {
        "data": date.today(),
        "total_aguardando": len(senhas),
        "por_tipo": por_tipo,
        "senhas": [senhas_service.to_response(s) for s in senhas],
    }


@senhas_router.get("/{codigo}", response_model=SenhaResponse)
def consultar_senha(codigo: str, db: Session = Depends(get_db)):
    try:
        senha = senhas_service.buscar_por_codigo(db, codigo)
    except ValueError as erro:
        raise HTTPException(status_code=404, detail=str(erro))
    return senhas_service.to_response(senha)
