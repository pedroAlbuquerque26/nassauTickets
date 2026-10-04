from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

load_dotenv()

APP_TITLE = os.getenv("APP_TITLE", "nassauTickets API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
EXPEDIENTE_INICIO = int(os.getenv("EXPEDIENTE_INICIO", "7"))
EXPEDIENTE_FIM = int(os.getenv("EXPEDIENTE_FIM", "17"))
NOT_ATTENDED_RATE = float(os.getenv("NOT_ATTENDED_RATE", "0.05"))
PANEL_LAST_CALLS = int(os.getenv("PANEL_LAST_CALLS", "5"))

_raw_origins = os.getenv("CORS_ORIGINS", "").strip()
CORS_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]
CORS_ALLOW_CREDENTIALS = bool(CORS_ORIGINS)


@asynccontextmanager
async def lifespan(_: FastAPI):
    from seed import init_database

    init_database()
    yield


app = FastAPI(title=APP_TITLE, version=APP_VERSION, lifespan=lifespan)

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )
