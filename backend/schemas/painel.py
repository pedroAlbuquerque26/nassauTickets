from datetime import datetime

from pydantic import BaseModel


class ChamadaPainel(BaseModel):
    codigo: str
    tipo: str
    guiche_numero: int
    chamada_em: datetime
    chamadas: int
    ultima_chamada: bool
    audio_texto: str


class PainelResponse(BaseModel):
    chamadas: list[ChamadaPainel]
    atualizado_em: datetime
