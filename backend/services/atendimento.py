from datetime import datetime

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from models import Guiche, Senha
from services.expediente import registrar_evento

ESTADOS_CHAMADA = ("CHAMADA", "CHAMADA_NOVAMENTE")


def _audio_texto(senha: Senha) -> str:
    prioridade = {"SP": "senha prioritaria", "SG": "senha geral", "SE": "senha de exames"}
    prefixo = "Ultima chamada, " if senha.chamadas >= 2 else ""
    guiche = senha.guiche.numero if senha.guiche else "?"
    return f"{prefixo}{prioridade[senha.tipo]}, senha {senha.codigo}, guiche {guiche}"


def _carregar_guiche(db: Session, guiche_id: int) -> Guiche:
    guiche = db.query(Guiche).filter(Guiche.id == guiche_id).first()
    if guiche is None:
        raise ValueError("Guiche nao encontrado")
    if not guiche.ativo:
        raise ValueError("Guiche inativo")
    return guiche


def _exigir_guiche_do_atendente(usuario: dict, guiche_id: int) -> None:
    """Atendente vinculado a um guiche so pode operar no guiche proprio."""
    guiche_vinculado = usuario.get("guiche_id")
    if guiche_vinculado is not None and guiche_vinculado != guiche_id:
        raise ValueError(
            f"Atendente vinculado ao guiche {guiche_vinculado}; "
            f"nao e permitido chamar no guiche {guiche_id}"
        )


def _carregar_senha(db: Session, senha_id: int) -> Senha:
    senha = db.query(Senha).filter(Senha.id == senha_id).first()
    if senha is None:
        raise ValueError("Senha nao encontrada")
    return senha


def _exigir_senha_do_guiche(senha: Senha, usuario: dict) -> None:
    """Atendente vinculado so opera senhas do proprio guiche."""
    guiche_vinculado = usuario.get("guiche_id")
    if guiche_vinculado is not None and senha.guiche_id != guiche_vinculado:
        raise ValueError(
            f"Senha {senha.codigo} nao pertence ao guiche {guiche_vinculado} do atendente"
        )


def chamar_proxima(db: Session, guiche_id: int, usuario: dict) -> Senha:
    _exigir_guiche_do_atendente(usuario, guiche_id)

    from services.fila import travar_fila

    travar_fila(db)

    _carregar_guiche(db, guiche_id)

    from services.fila import escolher_proxima

    chamadas_pendentes = (
        db.query(Senha)
        .filter(
            Senha.guiche_id == guiche_id,
            Senha.estado.in_(ESTADOS_CHAMADA),
            Senha.atendimento_inicio.is_(None),
        )
        .with_for_update()
        .all()
    )
    for pendente in chamadas_pendentes:
        pendente.estado = "NAO_COMPARECEU"
        pendente.nao_atendida = True
        registrar_evento(
            db,
            "ABANDONO",
            senha=pendente,
            usuario_id=usuario.get("id"),
            detalhe="Cliente nao compareceu e o atendente chamou a proxima senha",
        )

    senha = escolher_proxima(db)
    if senha is None:
        db.commit()
        raise ValueError("Nenhuma senha na fila")

    agora = datetime.now()
    senha.estado = "CHAMADA"
    senha.chamadas = 1
    senha.chamada1_em = agora
    senha.guiche_id = guiche_id
    senha.atendente_id = usuario.get("id")

    registrar_evento(
        db,
        "CHAMADA",
        senha=senha,
        guiche_id=guiche_id,
        usuario_id=usuario.get("id"),
        detalhe="Primeira chamada",
    )
    db.commit()
    db.refresh(senha)
    return senha


def chamar_novamente(db: Session, senha_id: int, usuario: dict) -> Senha:
    senha = _carregar_senha(db, senha_id)
    _exigir_senha_do_guiche(senha, usuario)
    if senha.estado not in ESTADOS_CHAMADA:
        raise ValueError(f"Estado invalido para chamar novamente: {senha.estado}")
    if senha.estado == "CHAMADA_NOVAMENTE":
        raise ValueError("Senha ja chamada novamente")

    senha.estado = "CHAMADA_NOVAMENTE"
    senha.chamadas = 2
    senha.chamada2_em = datetime.now()

    registrar_evento(
        db,
        "CHAMADA_NOVAMENTE",
        senha=senha,
        guiche_id=senha.guiche_id,
        usuario_id=usuario.get("id"),
        detalhe="Segunda chamada - Ultima chamada",
    )
    db.commit()
    db.refresh(senha)
    return senha


def iniciar_atendimento(db: Session, senha_id: int, usuario: dict) -> Senha:
    senha = _carregar_senha(db, senha_id)
    _exigir_senha_do_guiche(senha, usuario)
    if senha.estado not in ESTADOS_CHAMADA:
        raise ValueError(
            f"Estado invalido para iniciar atendimento: {senha.estado}"
        )

    senha.estado = "EM_ATENDIMENTO"
    senha.atendimento_inicio = datetime.now()

    registrar_evento(
        db,
        "ATENDIMENTO_INICIADO",
        senha=senha,
        guiche_id=senha.guiche_id,
        usuario_id=usuario.get("id"),
    )
    db.commit()
    db.refresh(senha)
    return senha


def finalizar_atendimento(db: Session, senha_id: int, usuario: dict) -> Senha:
    senha = _carregar_senha(db, senha_id)
    _exigir_senha_do_guiche(senha, usuario)
    if senha.estado != "EM_ATENDIMENTO":
        raise ValueError(f"Estado invalido para finalizar atendimento: {senha.estado}")

    senha.estado = "ATENDIDA"
    senha.atendimento_fim = datetime.now()

    registrar_evento(
        db,
        "ATENDIMENTO_FINALIZADO",
        senha=senha,
        guiche_id=senha.guiche_id,
        usuario_id=usuario.get("id"),
    )
    db.commit()
    db.refresh(senha)
    return senha


def registrar_nao_comparecimento(db: Session, senha_id: int, usuario: dict) -> Senha:
    senha = _carregar_senha(db, senha_id)
    _exigir_senha_do_guiche(senha, usuario)
    if senha.estado not in ESTADOS_CHAMADA:
        raise ValueError(f"Estado invalido para nao comparecimento: {senha.estado}")

    senha.estado = "NAO_COMPARECEU"
    senha.nao_atendida = True

    registrar_evento(
        db,
        "ABANDONO",
        senha=senha,
        guiche_id=senha.guiche_id,
        usuario_id=usuario.get("id"),
        detalhe="Cliente nao compareceu apos as chamadas",
    )
    db.commit()
    db.refresh(senha)
    return senha


def to_response(senha: Senha) -> dict:
    return {
        "id": senha.id,
        "codigo": senha.codigo,
        "tipo": senha.tipo,
        "estado": senha.estado,
        "chamadas": senha.chamadas,
        "guiche_id": senha.guiche_id,
        "guiche_numero": senha.guiche.numero if senha.guiche else None,
        "atendente_id": senha.atendente_id,
        "atendente_login": senha.atendente.login if senha.atendente else None,
        "chamada1_em": senha.chamada1_em,
        "chamada2_em": senha.chamada2_em,
        "atendimento_inicio": senha.atendimento_inicio,
        "atendimento_fim": senha.atendimento_fim,
        "audio_texto": _audio_texto(senha) if senha.chamada1_em else None,
    }


def executar_com_retry(db: Session, operacao, *args, **kwargs):
    ultimo_erro = None
    for _ in range(3):
        try:
            return operacao(db, *args, **kwargs)
        except (IntegrityError, OperationalError) as erro:
            db.rollback()
            ultimo_erro = erro
    raise RuntimeError(f"Falha apos tentativas de concorrencia: {ultimo_erro}")
