from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.atendimento import ProximaRequest, SenhaAtendimentoResponse
from services import atendimento as atendimento_service
from services.auth import require_atendente

atendimento_router = APIRouter(
    prefix="/atendimento",
    tags=["Atendimento"],
    dependencies=[Depends(require_atendente)],
)


@atendimento_router.post("/proxima", response_model=SenhaAtendimentoResponse)
def chamar_proxima(dados: ProximaRequest, current_user: dict = Depends(require_atendente), db: Session = Depends(get_db)):
    try:
        senha = atendimento_service.executar_com_retry(
            db, atendimento_service.chamar_proxima, dados.guiche_id, current_user
        )
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    except RuntimeError as erro:
        raise HTTPException(status_code=503, detail=str(erro))
    return atendimento_service.to_response(senha)


@atendimento_router.post("/{senha_id}/chamar-novamente", response_model=SenhaAtendimentoResponse)
def chamar_novamente(senha_id: int, current_user: dict = Depends(require_atendente), db: Session = Depends(get_db)):
    try:
        senha = atendimento_service.chamar_novamente(db, senha_id, current_user)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    return atendimento_service.to_response(senha)


@atendimento_router.post("/{senha_id}/iniciar", response_model=SenhaAtendimentoResponse)
def iniciar(senha_id: int, current_user: dict = Depends(require_atendente), db: Session = Depends(get_db)):
    try:
        senha = atendimento_service.iniciar_atendimento(db, senha_id, current_user)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    return atendimento_service.to_response(senha)


@atendimento_router.post("/{senha_id}/finalizar", response_model=SenhaAtendimentoResponse)
def finalizar(senha_id: int, current_user: dict = Depends(require_atendente), db: Session = Depends(get_db)):
    try:
        senha = atendimento_service.finalizar_atendimento(db, senha_id, current_user)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    return atendimento_service.to_response(senha)


@atendimento_router.post("/{senha_id}/nao-compareceu", response_model=SenhaAtendimentoResponse)
def nao_compareceu(senha_id: int, current_user: dict = Depends(require_atendente), db: Session = Depends(get_db)):
    try:
        senha = atendimento_service.registrar_nao_comparecimento(db, senha_id, current_user)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    return atendimento_service.to_response(senha)
