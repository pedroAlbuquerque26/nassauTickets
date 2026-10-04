from datetime import date, datetime

from sqlalchemy.orm import Session

from config import EXPEDIENTE_FIM, EXPEDIENTE_INICIO
from models import Auditoria, Senha

ESTADOS_PENDENTES = ("EMITIDA", "AGUARDANDO")
ESTADOS_CHAMADA = ("CHAMADA", "CHAMADA_NOVAMENTE")
ESTADOS_NAO_FINALIZADOS = (
    "EMITIDA",
    "AGUARDANDO",
    "CHAMADA",
    "CHAMADA_NOVAMENTE",
    "EM_ATENDIMENTO",
)


def dentro_do_expediente(momento: datetime = None) -> bool:
    momento = momento or datetime.now()
    return EXPEDIENTE_INICIO <= momento.hour < EXPEDIENTE_FIM


def registrar_evento(
    db: Session,
    evento: str,
    senha: Senha = None,
    guiche_id: int = None,
    usuario_id: int = None,
    detalhe: str = None,
) -> Auditoria:
    registro = Auditoria(
        senha_id=senha.id if senha is not None else None,
        guiche_id=guiche_id if guiche_id is not None else (senha.guiche_id if senha else None),
        usuario_id=usuario_id,
        evento=evento,
        detalhe=detalhe,
    )
    db.add(registro)
    return registro


def _descartar(db: Session, query, motivo: str) -> int:
    pendentes = query.all()
    for senha in pendentes:
        senha.estado = "NAO_COMPARECEU"
        senha.nao_atendida = True
        registrar_evento(db, "DESCARTE", senha=senha, detalhe=motivo)
    if pendentes:
        db.commit()
    return len(pendentes)


def descartar_expiradas(db: Session) -> int:
    """Descarta senhas nao finalizadas de dias anteriores (expediente encerrado)."""
    hoje = date.today()
    query = db.query(Senha).filter(
        Senha.estado.in_(ESTADOS_NAO_FINALIZADOS),
        Senha.data_emissao != hoje,
    )
    return _descartar(db, query, "Descarte de senha pendente de expediente encerrado")


def encerrar_expediente(db: Session) -> int:
    """Ao final do expediente, senhas que permanecerem na fila ou chamadas
    sem inicio de atendimento sao descartadas (atendimentos iniciados nao)."""
    hoje = date.today()
    query = db.query(Senha).filter(
        Senha.estado.in_(ESTADOS_PENDENTES + ESTADOS_CHAMADA),
        Senha.data_emissao == hoje,
    )
    return _descartar(db, query, "Descarte ao encerrar o expediente")


def status_expediente(db: Session) -> dict:
    hoje = date.today()
    descartadas = descartar_expiradas(db)
    aguardando = (
        db.query(Senha)
        .filter(Senha.estado == "AGUARDANDO", Senha.data_emissao == hoje)
        .count()
    )
    return {
        "aberto": dentro_do_expediente(),
        "inicio": f"{EXPEDIENTE_INICIO:02d}:00",
        "fim": f"{EXPEDIENTE_FIM:02d}:00",
        "data": hoje,
        "aguardando": aguardando,
        "pendentes_de_dias_anteriores_descartadas": descartadas,
        "agora": datetime.now(),
    }
