from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class SenhaDetalhada(BaseModel):
    codigo: str
    tipo: str
    estado: str
    emissao_em: datetime
    atendimento_inicio: Optional[datetime] = None
    atendimento_fim: Optional[datetime] = None
    guiche_numero: Optional[int] = None
    atendente_login: Optional[str] = None


class AuditoriaDetalhada(BaseModel):
    senha_codigo: Optional[str] = None
    atendente_login: Optional[str] = None
    guiche_numero: Optional[int] = None
    primeira_chamada: Optional[datetime] = None
    segunda_chamada: Optional[datetime] = None
    inicio_atendimento: Optional[datetime] = None
    fim_atendimento: Optional[datetime] = None


class TempoMedio(BaseModel):
    tipo: str
    tm_medio_minutos: Optional[float] = None
    tm_esperado_minutos: float
    atendimentos: int


class Quantitativos(BaseModel):
    emitidas: int
    atendidas: int
    nao_atendidas: int
    emitidas_por_tipo: dict[str, int]
    atendidas_por_tipo: dict[str, int]


class RelatorioResponse(BaseModel):
    periodo: str
    data: Optional[date] = None
    ano: Optional[int] = None
    mes: Optional[int] = None
    quantitativos: Quantitativos
    tempo_medio: list[TempoMedio]
    tempo_medio_geral_minutos: Optional[float] = None
    senhas: list[SenhaDetalhada]
    auditoria: list[AuditoriaDetalhada]


class AuditoriaResponse(BaseModel):
    eventos: list[AuditoriaDetalhada]
    total: int


class DesempenhoPorTipo(BaseModel):
    emitidas: int
    atendidas: int
    tm_medio_minutos: Optional[float] = None
    tm_esperado_minutos: float
    desvio_tm_minutos: Optional[float] = None
    custo_estimado_atendimentos: Optional[float] = None


class DesempenhoResponse(BaseModel):
    data: date
    emitidas: int
    atendidas: int
    nao_atendidas: int
    abandonadas_apos_2_chamadas: int
    aguardando: int
    taxa_atendimento: Optional[float] = None
    taxa_nao_atendimento: Optional[float] = None
    taxa_abandono: Optional[float] = None
    senhas_por_hora_expediente: Optional[float] = None
    atendimentos_por_hora_expediente: Optional[float] = None
    tempo_medio_geral_minutos: Optional[float] = None
    custo_estimado_total: Optional[float] = None
    custo_minuto_atendimento: float
    por_tipo: dict[str, DesempenhoPorTipo]
    eventos_auditoria: int
