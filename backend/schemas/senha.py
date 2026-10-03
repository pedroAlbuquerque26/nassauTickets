from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EmitirRequest(BaseModel):
    tipo: str = Field(pattern="^(SP|SG|SE)$")


class SenhaResponse(BaseModel):
    id: int
    codigo: str
    tipo: str
    sequencia: int
    data_emissao: date
    emissao_em: datetime
    estado: str
    chamadas: int
    guiche_id: Optional[int] = None
    guiche_numero: Optional[int] = None
    atendimento_inicio: Optional[datetime] = None
    atendimento_fim: Optional[datetime] = None
    nao_atendida: bool

    model_config = ConfigDict(from_attributes=True)


class FilaResponse(BaseModel):
    data: date
    total_aguardando: int
    por_tipo: dict[str, int]
    senhas: list[SenhaResponse]
