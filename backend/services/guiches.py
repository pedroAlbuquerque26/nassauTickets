from sqlalchemy.orm import Session

from models import Guiche


def listar(db: Session, incluir_inativos: bool = True) -> list[Guiche]:
    query = db.query(Guiche)
    if not incluir_inativos:
        query = query.filter(Guiche.ativo.is_(True))
    return query.order_by(Guiche.numero.asc()).all()


def criar(db: Session, dados: dict) -> Guiche:
    if db.query(Guiche).filter(Guiche.numero == dados["numero"]).first():
        raise ValueError(f"Guiche ja cadastrado: {dados['numero']}")
    guiche = Guiche(numero=dados["numero"], nome=dados["nome"], ativo=dados.get("ativo", True))
    db.add(guiche)
    db.commit()
    db.refresh(guiche)
    return guiche


def atualizar(db: Session, guiche_id: int, dados: dict) -> Guiche:
    guiche = db.query(Guiche).filter(Guiche.id == guiche_id).first()
    if guiche is None:
        raise ValueError("Guiche nao encontrado")

    if dados.get("numero") is not None:
        duplicado = (
            db.query(Guiche)
            .filter(Guiche.numero == dados["numero"], Guiche.id != guiche_id)
            .first()
        )
        if duplicado:
            raise ValueError(f"Guiche ja cadastrado: {dados['numero']}")

    for campo in ("numero", "nome", "ativo"):
        valor = dados.get(campo)
        if valor is not None:
            setattr(guiche, campo, valor)

    db.commit()
    db.refresh(guiche)
    return guiche


def remover(db: Session, guiche_id: int) -> None:
    guiche = db.query(Guiche).filter(Guiche.id == guiche_id).first()
    if guiche is None:
        raise ValueError("Guiche nao encontrado")
    if guiche.senhas:
        raise ValueError("Guiche possui senhas atendidas; desative-o em vez de excluir")
    if guiche.atendentes:
        raise ValueError("Guiche possui atendentes vinculados; desative-o em vez de excluir")
    if guiche.eventos:
        raise ValueError("Guiche possui eventos de auditoria; desative-o em vez de excluir")
    db.delete(guiche)
    db.commit()
