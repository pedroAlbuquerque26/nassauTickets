from datetime import date, datetime

from sqlalchemy.orm import Session

from models import ControleFila, Senha


def travar_fila(db: Session) -> None:
    """Trava a linha de controle da fila, serializando escolhas simultaneas."""
    controle = (
        db.query(ControleFila)
        .filter(ControleFila.id == 1)
        .with_for_update()
        .first()
    )
    if controle is None:
        controle = ControleFila(id=1)
        db.add(controle)
        db.flush()
    controle.atualizado_em = datetime.now()


def ordem_prioridade(ultimo_tipo: str = None) -> list[str]:
    """[SP] -> [SE|SG] -> [SP] -> [SE|SG]"""
    if ultimo_tipo == "SP":
        return ["SE", "SG", "SP"]
    return ["SP", "SE", "SG"]


def ultimo_tipo_chamado(db: Session, data: date = None) -> str:
    data = data or date.today()
    ultima = (
        db.query(Senha)
        .filter(Senha.chamada1_em.isnot(None), Senha.data_emissao == data)
        .order_by(Senha.chamada1_em.desc(), Senha.id.desc())
        .first()
    )
    return ultima.tipo if ultima else None


def escolher_proxima(db: Session, data: date = None) -> Senha:
    data = data or date.today()
    for tipo in ordem_prioridade(ultimo_tipo_chamado(db, data)):
        senha = (
            db.query(Senha)
            .filter(Senha.estado == "AGUARDANDO", Senha.tipo == tipo, Senha.data_emissao == data)
            .order_by(Senha.emissao_em.asc(), Senha.sequencia.asc())
            .with_for_update(skip_locked=True)
            .first()
        )
        if senha is not None:
            return senha
    return None
