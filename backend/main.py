from config import app
from routers import (
    atendimento,
    auth,
    expediente,
    guiches,
    painel,
    relatorios,
    senhas,
    usuarios,
)

app.include_router(auth.auth_router)
app.include_router(usuarios.usuarios_router)
app.include_router(guiches.guiches_router)
app.include_router(senhas.senhas_router)
app.include_router(atendimento.atendimento_router)
app.include_router(painel.painel_router)
app.include_router(expediente.expediente_router)
app.include_router(relatorios.relatorios_router)


@app.get("/")
def home():
    return {"message": "nassauTickets API funcionando", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
