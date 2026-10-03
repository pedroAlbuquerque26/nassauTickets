from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    login: str
    senha: str


class UsuarioBase(BaseModel):
    login: str
    nome: str
    perfil: str = "ATENDENTE"
    guiche_id: Optional[int] = None
    ativo: bool = True


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    perfil: Optional[str] = None
    guiche_id: Optional[int] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = None


class UsuarioResponse(BaseModel):
    id: int
    login: str
    nome: str
    perfil: str
    guiche_id: Optional[int] = None
    ativo: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class GuicheBase(BaseModel):
    numero: int
    nome: str
    ativo: bool = True


class GuicheCreate(GuicheBase):
    pass


class GuicheUpdate(BaseModel):
    numero: Optional[int] = None
    nome: Optional[str] = None
    ativo: Optional[bool] = None


class GuicheResponse(BaseModel):
    id: int
    numero: int
    nome: str
    ativo: bool

    model_config = ConfigDict(from_attributes=True)
