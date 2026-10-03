from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base

SENHA_TIPOS = ("SP", "SG", "SE")

ESTADOS = (
    "EMITIDA",
    "AGUARDANDO",
    "CHAMADA",
    "CHAMADA_NOVAMENTE",
    "EM_ATENDIMENTO",
    "ATENDIDA",
    "NAO_COMPARECEU",
)

PERFIS = ("ATENDENTE", "GESTOR")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    login = Column(String(100), nullable=False, unique=True, index=True)
    nome = Column(String(150), nullable=False)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(Enum(*PERFIS, name="perfil_enum"), nullable=False, default="ATENDENTE")
    guiche_id = Column(Integer, ForeignKey("guiches.id"), nullable=True)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime, nullable=False, default=datetime.now)

    guiche = relationship("Guiche", backref="atendentes")


class Guiche(Base):
    __tablename__ = "guiches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    numero = Column(Integer, nullable=False, unique=True, index=True)
    nome = Column(String(100), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)


class Sequencia(Base):
    __tablename__ = "sequencias"
    __table_args__ = (UniqueConstraint("data", "tipo", name="uq_sequencia_data_tipo"),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    data = Column(Date, nullable=False, index=True)
    tipo = Column(Enum(*SENHA_TIPOS, name="sequencia_tipo_enum"), nullable=False)
    valor = Column(Integer, nullable=False, default=0)


class Senha(Base):
    __tablename__ = "senhas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(20), nullable=False, unique=True, index=True)
    tipo = Column(Enum(*SENHA_TIPOS, name="senha_tipo_enum"), nullable=False, index=True)
    sequencia = Column(Integer, nullable=False)
    data_emissao = Column(Date, nullable=False, index=True)
    emissao_em = Column(DateTime, nullable=False, default=datetime.now)
    estado = Column(
        Enum(*ESTADOS, name="senha_estado_enum"),
        nullable=False,
        default="EMITIDA",
        index=True,
    )
    guiche_id = Column(Integer, ForeignKey("guiches.id"), nullable=True)
    atendente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    chamadas = Column(Integer, nullable=False, default=0)
    chamada1_em = Column(DateTime, nullable=True)
    chamada2_em = Column(DateTime, nullable=True)
    atendimento_inicio = Column(DateTime, nullable=True)
    atendimento_fim = Column(DateTime, nullable=True)
    nao_atendida = Column(Boolean, nullable=False, default=False)

    guiche = relationship("Guiche", backref="senhas")
    atendente = relationship("Usuario", backref="senhas")


class ControleFila(Base):
    """Unica linha (id=1) travada com SELECT ... FOR UPDATE para serializar
    a escolha da proxima senha quando varios atendentes chamam ao mesmo tempo."""

    __tablename__ = "controle_fila"

    id = Column(Integer, primary_key=True, autoincrement=False)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.now)


class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    senha_id = Column(Integer, ForeignKey("senhas.id"), nullable=True)
    guiche_id = Column(Integer, ForeignKey("guiches.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    evento = Column(String(50), nullable=False, index=True)
    detalhe = Column(String(255), nullable=True)
    criado_em = Column(DateTime, nullable=False, default=datetime.now, index=True)

    senha = relationship("Senha", backref="eventos")
    guiche = relationship("Guiche", backref="eventos")
    usuario = relationship("Usuario", backref="eventos")
