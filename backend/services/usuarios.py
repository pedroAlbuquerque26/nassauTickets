from passlib.context import CryptContext
from sqlalchemy.orm import Session

from models import PERFIS, Guiche, Usuario
from services.auth import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _verificar_guiche(db: Session, guiche_id: int = None) -> None:
    if guiche_id is None:
        return
    guiche = db.query(Guiche).filter(Guiche.id == guiche_id).first()
    if guiche is None:
        raise ValueError("Guiche nao encontrado")


def listar(db: Session) -> list[Usuario]:
    return db.query(Usuario).order_by(Usuario.login.asc()).all()


def criar(db: Session, dados: dict) -> Usuario:
    if dados.get("perfil") not in PERFIS:
        raise ValueError(f"Perfil invalido: {dados.get('perfil')}")
    if db.query(Usuario).filter(Usuario.login == dados["login"]).first():
        raise ValueError(f"Login ja cadastrado: {dados['login']}")
    _verificar_guiche(db, dados.get("guiche_id"))

    usuario = Usuario(
        login=dados["login"],
        nome=dados["nome"],
        senha_hash=pwd_context.hash(dados["senha"]),
        perfil=dados["perfil"],
        guiche_id=dados.get("guiche_id"),
        ativo=dados.get("ativo", True),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def atualizar(db: Session, usuario_id: int, dados: dict) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise ValueError("Usuario nao encontrado")

    if "perfil" in dados and dados["perfil"] is not None and dados["perfil"] not in PERFIS:
        raise ValueError(f"Perfil invalido: {dados['perfil']}")
    if "guiche_id" in dados:
        _verificar_guiche(db, dados["guiche_id"])

    for campo in ("nome", "perfil", "guiche_id", "ativo"):
        if campo in dados:
            setattr(usuario, campo, dados[campo])
    if dados.get("senha"):
        usuario.senha_hash = pwd_context.hash(dados["senha"])

    db.commit()
    db.refresh(usuario)
    return usuario


def remover(db: Session, usuario_id: int) -> None:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise ValueError("Usuario nao encontrado")
    if usuario.senhas:
        raise ValueError(
            "Usuario possui historico de atendimentos; desative-o em vez de excluir"
        )
    if usuario.eventos:
        raise ValueError(
            "Usuario possui eventos de auditoria; desative-o em vez de excluir"
        )
    db.delete(usuario)
    db.commit()


def login(db: Session, login: str, senha: str) -> dict:
    usuario = db.query(Usuario).filter(Usuario.login == login).first()
    if usuario is None or not pwd_context.verify(senha, usuario.senha_hash):
        raise ValueError("Login ou senha invalidos")
    if not usuario.ativo:
        raise ValueError("Usuario inativo")

    token = create_access_token(
        {
            "sub": usuario.login,
            "id": usuario.id,
            "nome": usuario.nome,
            "perfil": usuario.perfil,
            "guiche_id": usuario.guiche_id,
        }
    )
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}
