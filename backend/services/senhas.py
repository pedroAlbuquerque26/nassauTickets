import random
from datetime import date, datetime

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from config import NOT_ATTENDED_RATE
from models import SENHA_TIPOS, Sequencia, Senha
from services.expediente import registrar_evento


def formatar_codigo(data: date, tipo: str, sequencia: int) -> str:
    return f"{data.strftime('%y%m%d')}-{tipo}{sequencia:03d}"


def proxima_sequencia(db: Session, data: date, tipo: str) -> int:
    sequencia = (
        db.query(Sequencia)
        .filter(Sequencia.data == data, Sequencia.tipo == tipo)
        .with_for_update()
        .first()
    )
    if sequencia is None:
        sequencia = Sequencia(data=data, tipo=tipo, valor=0)
        db.add(sequencia)
        db.flush()
    sequencia.valor += 1
    return sequencia.valor


def _emitir(db: Session, tipo: str) -> Senha:
    hoje = date.today()
    agora = datetime.now()
    sequencia = proxima_sequencia(db, hoje, tipo)

    senha = Senha(
        codigo=formatar_codigo(hoje, tipo, sequencia),
        tipo=tipo,
        sequencia=sequencia,
        data_emissao=hoje,
        emissao_em=agora,
        estado="EMITIDA",
    )
    db.add(senha)
    db.flush()

    registrar_evento(db, "EMITIDA", senha=senha, detalhe=f"Emissao via totem: {senha.codigo}")

    descartada = random.random() < NOT_ATTENDED_RATE
    if descartada:
        senha.estado = "NAO_COMPARECEU"
        senha.nao_atendida = True
        registrar_evento(
            db,
            "DESCARTE",
            senha=senha,
            detalhe="Regra dos 5%: senha descartada sem executar o atendimento",
        )
    else:
        senha.estado = "AGUARDANDO"

    db.commit()
    db.refresh(senha)
    return senha


def emitir_senha(db: Session, tipo: str) -> Senha:
    if tipo not in SENHA_TIPOS:
        raise ValueError(f"Tipo de senha invalido: {tipo}")

    ultimo_erro = None
    for _ in range(3):
        try:
            return _emitir(db, tipo)
        except (IntegrityError, OperationalError) as erro:
            db.rollback()
            ultimo_erro = erro

    raise RuntimeError(f"Falha ao emitir senha apos tentativas de concorrencia: {ultimo_erro}")


def listar_fila(db: Session) -> list[Senha]:
    hoje = date.today()
    return (
        db.query(Senha)
        .filter(Senha.estado == "AGUARDANDO", Senha.data_emissao == hoje)
        .order_by(Senha.emissao_em.asc(), Senha.sequencia.asc())
        .all()
    )


def buscar_por_codigo(db: Session, codigo: str) -> Senha:
    senha = db.query(Senha).filter(Senha.codigo == codigo).first()
    if senha is None:
        raise ValueError(f"Senha nao encontrada: {codigo}")
    return senha


def to_response(senha: Senha) -> dict:
    return {
        "id": senha.id,
        "codigo": senha.codigo,
        "tipo": senha.tipo,
        "sequencia": senha.sequencia,
        "data_emissao": senha.data_emissao,
        "emissao_em": senha.emissao_em,
        "estado": senha.estado,
        "chamadas": senha.chamadas,
        "guiche_id": senha.guiche_id,
        "guiche_numero": senha.guiche.numero if senha.guiche else None,
        "atendimento_inicio": senha.atendimento_inicio,
        "atendimento_fim": senha.atendimento_fim,
        "nao_atendida": senha.nao_atendida,
    }
