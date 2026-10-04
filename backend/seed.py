import os
import sys
import time

from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy import text

from database import Base, Session, engine
from models import ControleFila, Guiche, Usuario
from services.expediente import descartar_expiradas

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

GUICHES = [
    (1, "Guiche 1"),
    (2, "Guiche 2"),
    (3, "Guiche 3"),
    (4, "Guiche 4"),
    (5, "Guiche 5"),
]

GESTOR_LOGIN = os.getenv("SEED_GESTOR_LOGIN", "admin")
GESTOR_SENHA = os.getenv("SEED_GESTOR_SENHA", "admin123")
GESTOR_NOME = os.getenv("SEED_GESTOR_NOME", "Gestor")
ATENDENTE_LOGIN = os.getenv("SEED_ATENDENTE_LOGIN", "atendente")
ATENDENTE_SENHA = os.getenv("SEED_ATENDENTE_SENHA", "atendente123")
ATENDENTE_NOME = os.getenv("SEED_ATENDENTE_NOME", "Atendente")
# Especificacao: um unico atendente com perfil adicional de gestor
ATENDENTE_PERFIL = os.getenv("SEED_ATENDENTE_PERFIL", "GESTOR")


def seed_guiches(db) -> None:
    for numero, nome in GUICHES:
        existente = db.query(Guiche).filter(Guiche.numero == numero).first()
        if existente:
            continue
        db.add(Guiche(numero=numero, nome=nome, ativo=True))
    db.commit()


def seed_controle(db) -> None:
    if db.query(ControleFila).filter(ControleFila.id == 1).first() is None:
        db.add(ControleFila(id=1))
    db.commit()


def seed_usuarios(db) -> None:
    guiche_1 = db.query(Guiche).filter(Guiche.numero == 1).first()
    guiche_1_id = guiche_1.id if guiche_1 else None

    gestor = db.query(Usuario).filter(Usuario.login == GESTOR_LOGIN).first()
    if not gestor:
        db.add(
            Usuario(
                login=GESTOR_LOGIN,
                nome=GESTOR_NOME,
                senha_hash=pwd_context.hash(GESTOR_SENHA),
                perfil="GESTOR",
                ativo=True,
            )
        )

    atendente = db.query(Usuario).filter(Usuario.login == ATENDENTE_LOGIN).first()
    if not atendente:
        db.add(
            Usuario(
                login=ATENDENTE_LOGIN,
                nome=ATENDENTE_NOME,
                senha_hash=pwd_context.hash(ATENDENTE_SENHA),
                perfil=ATENDENTE_PERFIL,
                guiche_id=guiche_1_id,
                ativo=True,
            )
        )
    else:
        if atendente.perfil != ATENDENTE_PERFIL:
            atendente.perfil = ATENDENTE_PERFIL
        if guiche_1_id is not None and atendente.guiche_id != guiche_1_id:
            atendente.guiche_id = guiche_1_id

    db.commit()


def aguardar_banco(tentativas: int = 30, intervalo: float = 1.0) -> None:
    ultimo_erro = None
    for _ in range(tentativas):
        try:
            with engine.connect() as conexao:
                conexao.execute(text("SELECT 1"))
            return
        except Exception as erro:
            ultimo_erro = erro
            time.sleep(intervalo)
    raise RuntimeError(f"Banco de dados indisponivel: {ultimo_erro}")


def init_database() -> None:
    aguardar_banco()
    Base.metadata.create_all(bind=engine)

    db = Session()
    try:
        descartar_expiradas(db)
        seed_guiches(db)
        seed_controle(db)
        seed_usuarios(db)
    finally:
        db.close()


if __name__ == "__main__":
    try:
        init_database()
        print("Banco criado e populado com sucesso.")
    except Exception as erro:
        print(f"Erro ao inicializar o banco: {erro}")
        sys.exit(1)
