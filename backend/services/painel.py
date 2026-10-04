from datetime import date, datetime

from sqlalchemy.orm import Session

from config import PANEL_LAST_CALLS
from models import Senha


def _audio_texto(senha: Senha) -> str:
    prioridade = {"SP": "senha prioritaria", "SG": "senha geral", "SE": "senha de exames"}
    prefixo = "Ultima chamada, " if senha.chamadas >= 2 else ""
    guiche = senha.guiche.numero if senha.guiche else "?"
    return f"{prefixo}{prioridade[senha.tipo]}, senha {senha.codigo}, guiche {guiche}"


def _ultima_chamada_em(senha: Senha) -> datetime:
    return senha.chamada2_em or senha.chamada1_em


def ultimas_chamadas(db: Session, data: date = None) -> list[dict]:
    data = data or date.today()
    senhas = (
        db.query(Senha)
        .filter(Senha.chamada1_em.isnot(None), Senha.data_emissao == data)
        .all()
    )
    senhas = sorted(senhas, key=_ultima_chamada_em, reverse=True)[:PANEL_LAST_CALLS]
    return [
        {
            "codigo": senha.codigo,
            "tipo": senha.tipo,
            "guiche_numero": senha.guiche.numero if senha.guiche else 0,
            "chamada_em": _ultima_chamada_em(senha),
            "chamadas": senha.chamadas,
            "ultima_chamada": senha.chamadas >= 2,
            "audio_texto": _audio_texto(senha),
        }
        for senha in senhas
    ]


def painel(db: Session) -> dict:
    return {
        "chamadas": ultimas_chamadas(db),
        "atualizado_em": datetime.now(),
    }
