from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProximaRequest(BaseModel):
    guiche_id: int = Field(gt=0)


class SenhaAtendimentoResponse(BaseModel):
    id: int
    codigo: str
    tipo: str
    estado: str
    chamadas: int
    guiche_id: Optional[int] = None
    guiche_numero: Optional[int] = None
    atendente_id: Optional[int] = None
    atendente_login: Optional[str] = None
    chamada1_em: Optional[datetime] = None
    chamada2_em: Optional[datetime] = None
    atendimento_inicio: Optional[datetime] = None
    atendimento_fim: Optional[datetime] = None
    audio_texto: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
