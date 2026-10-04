from calendar import monthrange
from datetime import date, datetime

from sqlalchemy.orm import Session

from config import EXPEDIENTE_FIM, EXPEDIENTE_INICIO
from models import Auditoria, Senha

TM_ESPERADO = {"SP": 15.0, "SG": 5.0, "SE": 2.0}
CUSTO_MINUTO_POR_ATENDIMENTO = 3.5


def _minutos(inicio: datetime, fim: datetime) -> float:
    return round((fim - inicio).total_seconds() / 60.0, 2)


def _tempo_medio(senhas: list[Senha], tipo: str = None) -> tuple[float | None, int]:
    atendidas = [
        s
        for s in senhas
        if s.estado == "ATENDIDA" and s.atendimento_inicio and s.atendimento_fim
        and (tipo is None or s.tipo == tipo)
    ]
    if not atendidas:
        return None, 0
    media = sum(_minutos(s.atendimento_inicio, s.atendimento_fim) for s in atendidas) / len(atendidas)
    return round(media, 2), len(atendidas)


def _quantitativos(senhas: list[Senha]) -> dict:
    emitidas_por_tipo = {tipo: 0 for tipo in ("SP", "SG", "SE")}
    atendidas_por_tipo = {tipo: 0 for tipo in ("SP", "SG", "SE")}
    atendidas = 0
    nao_atendidas = 0

    for senha in senhas:
        emitidas_por_tipo[senha.tipo] += 1
        if senha.estado == "ATENDIDA":
            atendidas += 1
            atendidas_por_tipo[senha.tipo] += 1
        elif senha.estado == "NAO_COMPARECEU":
            nao_atendidas += 1

    return {
        "emitidas": len(senhas),
        "atendidas": atendidas,
        "nao_atendidas": nao_atendidas,
        "emitidas_por_tipo": emitidas_por_tipo,
        "atendidas_por_tipo": atendidas_por_tipo,
    }


def _preenchido_para_relatorio(s: Senha) -> bool:
    """PDF: campos de atendimento em branco apenas para nao atendidas.
    Chamadas e atendimentos em curso mantem guiche/atendente."""
    if s.estado == "NAO_COMPARECEU":
        return False
    if s.estado in ("EMITIDA", "AGUARDANDO") and s.chamada1_em is None:
        return False
    return True


def _detalhado(senhas: list[Senha]) -> list[dict]:
    return [
        {
            "codigo": s.codigo,
            "tipo": s.tipo,
            "estado": s.estado,
            "emissao_em": s.emissao_em,
            "atendimento_inicio": s.atendimento_inicio if s.estado == "ATENDIDA" else None,
            "atendimento_fim": s.atendimento_fim if s.estado == "ATENDIDA" else None,
            "guiche_numero": (
                s.guiche.numero
                if _preenchido_para_relatorio(s) and s.guiche is not None
                else None
            ),
            "atendente_login": (
                s.atendente.login
                if _preenchido_para_relatorio(s) and s.atendente is not None
                else None
            ),
        }
        for s in senhas
    ]


def _auditoria(senhas: list[Senha]) -> list[dict]:
    chamadas = sorted(
        [s for s in senhas if s.chamada1_em is not None],
        key=lambda s: s.chamada1_em,
    )
    return [
        {
            "senha_codigo": s.codigo,
            "atendente_login": s.atendente.login if s.atendente else None,
            "guiche_numero": s.guiche.numero if s.guiche else None,
            "primeira_chamada": s.chamada1_em,
            "segunda_chamada": s.chamada2_em,
            "inicio_atendimento": s.atendimento_inicio,
            "fim_atendimento": s.atendimento_fim,
        }
        for s in chamadas
    ]


def _montar_relatorio(senhas: list[Senha], periodo: str, **filtros) -> dict:
    tempo_medio = []
    for tipo in ("SP", "SG", "SE"):
        media, total = _tempo_medio(senhas, tipo)
        tempo_medio.append(
            {
                "tipo": tipo,
                "tm_medio_minutos": media,
                "tm_esperado_minutos": TM_ESPERADO[tipo],
                "atendimentos": total,
            }
        )
    media_geral, _ = _tempo_medio(senhas)

    return {
        "periodo": periodo,
        **filtros,
        "quantitativos": _quantitativos(senhas),
        "tempo_medio": tempo_medio,
        "tempo_medio_geral_minutos": media_geral,
        "senhas": _detalhado(senhas),
        "auditoria": _auditoria(senhas),
    }


def relatorio_diario(db: Session, data: date) -> dict:
    senhas = (
        db.query(Senha)
        .filter(Senha.data_emissao == data)
        .order_by(Senha.emissao_em.asc())
        .all()
    )
    return _montar_relatorio(senhas, "diario", data=data)


def relatorio_mensal(db: Session, ano: int, mes: int) -> dict:
    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])
    senhas = (
        db.query(Senha)
        .filter(Senha.data_emissao >= primeiro_dia, Senha.data_emissao <= ultimo_dia)
        .order_by(Senha.emissao_em.asc())
        .all()
    )
    return _montar_relatorio(senhas, "mensal", ano=ano, mes=mes)


def relatorio_auditoria(db: Session, data: date) -> dict:
    senhas = (
        db.query(Senha)
        .filter(Senha.data_emissao == data, Senha.chamada1_em.isnot(None))
        .order_by(Senha.chamada1_em.asc())
        .all()
    )
    eventos = _auditoria(senhas)
    return {"eventos": eventos, "total": len(eventos)}


def _taxa(valor: float, base: int) -> float | None:
    if base == 0:
        return None
    return round(valor / base, 4)


def relatorio_desempenho(db: Session, data: date = None) -> dict:
    """Proposta de quantificacao e acompanhamento do desempenho dos atendimentos."""
    data = data or date.today()
    senhas = (
        db.query(Senha)
        .filter(Senha.data_emissao == data)
        .order_by(Senha.emissao_em.asc())
        .all()
    )

    emitidas = len(senhas)
    atendidas = [s for s in senhas if s.estado == "ATENDIDA"]
    nao_atendidas = [s for s in senhas if s.estado == "NAO_COMPARECEU"]
    abandonadas = [s for s in senhas if s.chamadas >= 2 and s.estado == "NAO_COMPARECEU"]
    em_fila = [s for s in senhas if s.estado in ("EMITIDA", "AGUARDANDO")]
    horas_expediente = max(EXPEDIENTE_FIM - EXPEDIENTE_INICIO, 1)

    por_tipo = {}
    for tipo in ("SP", "SG", "SE"):
        emitidas_tipo = [s for s in senhas if s.tipo == tipo]
        atendidas_tipo = [s for s in emitidas_tipo if s.estado == "ATENDIDA"]
        media, total = _tempo_medio(emitidas_tipo, tipo)
        tm_esperado = TM_ESPERADO[tipo]
        desvio = None
        if media is not None:
            desvio = round(media - tm_esperado, 2)
        custo_total = None
        if media is not None and total:
            custo_total = round(media * CUSTO_MINUTO_POR_ATENDIMENTO * total, 2)
        por_tipo[tipo] = {
            "emitidas": len(emitidas_tipo),
            "atendidas": len(atendidas_tipo),
            "tm_medio_minutos": media,
            "tm_esperado_minutos": tm_esperado,
            "desvio_tm_minutos": desvio,
            "custo_estimado_atendimentos": custo_total,
        }

    media_geral, total_geral = _tempo_medio(senhas)
    custo_geral = None
    if media_geral is not None and total_geral:
        custo_geral = round(media_geral * CUSTO_MINUTO_POR_ATENDIMENTO * total_geral, 2)

    return {
        "data": data,
        "emitidas": emitidas,
        "atendidas": len(atendidas),
        "nao_atendidas": len(nao_atendidas),
        "abandonadas_apos_2_chamadas": len(abandonadas),
        "aguardando": len(em_fila),
        "taxa_atendimento": _taxa(len(atendidas), emitidas),
        "taxa_nao_atendimento": _taxa(len(nao_atendidas), emitidas),
        "taxa_abandono": _taxa(len(abandonadas), emitidas),
        "senhas_por_hora_expediente": _taxa(emitidas, horas_expediente),
        "atendimentos_por_hora_expediente": _taxa(len(atendidas), horas_expediente),
        "tempo_medio_geral_minutos": media_geral,
        "custo_estimado_total": custo_geral,
        "custo_minuto_atendimento": CUSTO_MINUTO_POR_ATENDIMENTO,
        "por_tipo": por_tipo,
        "eventos_auditoria": db.query(Auditoria).filter(Auditoria.criado_em >= datetime.combine(data, datetime.min.time())).count(),
    }
