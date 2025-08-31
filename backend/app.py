import os
import json
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import time
import uuid
from pydantic import BaseModel


def read_secret(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            value = f.read().strip()
            return value or None
    except FileNotFoundError:
        return None
    except Exception:
        # Do not leak details
        return None


def get_api_key() -> str:
    # Prefer Swarm secret if available
    secret = read_secret("/run/secrets/openai_api_key")
    if secret:
        return secret
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key
    raise HTTPException(status_code=500, detail={"error": "OPENAI_API_KEY not configured"})


MODEL = os.getenv("MODEL", "gpt-realtime-2025-08-28")
VOICE = os.getenv("VOICE", "marin")
SILENCE_MS = int(os.getenv("SILENCE_MS", "600"))

# Persona instructions (PT-BR), acessível para pessoas cegas.
INSTRUCTIONS = os.getenv(
    "INSTRUCTIONS",
    (
        "Você é o Farol (PT-BR). Ajude pessoas com deficiência visual com respostas claras, objetivas e acolhedoras. "
        "Use linguagem simples, descreva informações essenciais de forma auditiva acessível e confirme entendimento quando necessário. "
        "Evite jargões. Quando útil, liste passos curtos e numerados."
    ),
)


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("farol-backend")

app = FastAPI(title="Farol Realtime Backend", version="0.1.0")

# CORS: permitir origens do Streamlit (para demo: *)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/health")
async def health():
    logger.debug("Health check")
    return {"status": "ok"}


@app.post("/session")
async def create_session():
    api_key = get_api_key()
    started = time.time()
    rid = str(uuid.uuid4())
    logger.info(
        "session.request start %s",
        json.dumps({"rid": rid, "model": MODEL, "voice": VOICE, "silence_ms": SILENCE_MS}, ensure_ascii=False),
    )

    payload = {
        "model": MODEL,
        "voice": VOICE,
        "modalities": ["audio", "text"],
        "instructions": INSTRUCTIONS,
        "turn_detection": {
            "type": "server_vad",
            "silence_duration_ms": SILENCE_MS,
        },
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "realtime=v1",
    }

    url = "https://api.openai.com/v1/realtime/sessions"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            # If OpenAI returns an error, surface the body when possible
            if resp.status_code >= 400:
                detail: object
                try:
                    detail = resp.json()
                except Exception:
                    detail = {"status": resp.status_code, "message": resp.text[:500]}
                logger.warning(
                    "session.request error %s",
                    json.dumps({"rid": rid, "status": resp.status_code, "detail": detail}, ensure_ascii=False),
                )
                raise HTTPException(status_code=resp.status_code, detail=detail)
            data = resp.json()
            elapsed_ms = int((time.time() - started) * 1000)
            # Do not log secrets
            safe = {
                k: v
                for k, v in data.items()
                if k not in {"client_secret", "server_secret", "key", "token"}
            }
            session_id = safe.get("id") if isinstance(safe, dict) else None
            logger.info(
                "session.request ok %s",
                json.dumps({"rid": rid, "elapsed_ms": elapsed_ms, "session_id": session_id, "meta": safe}, ensure_ascii=False),
            )
            # Return the session JSON as-is
            return data
    except HTTPException:
        raise
    except httpx.RequestError as e:
        logger.exception("session.request network_error")
        raise HTTPException(status_code=502, detail={"error": "Network error contacting OpenAI", "detail": str(e)})
    except Exception as e:
        logger.exception("session.request unexpected_error")
        raise HTTPException(status_code=500, detail={"error": "Unexpected server error"})

@app.get("/webrtc", response_class=HTMLResponse)
async def webrtc_page(request: Request):
    # Expose model for the JS via template context
    client_id = str(uuid.uuid4())
    logger.info(
        "webrtc.page %s",
        json.dumps({"client_id": client_id, "client": request.client.host if request.client else None}, ensure_ascii=False),
    )
    return templates.TemplateResponse(
        "webrtc.html",
        {
            "request": request,
            "model": MODEL,
            "voice": VOICE,
            "silence_ms": SILENCE_MS,
            "client_id": client_id,
        },
    )


class LogEvent(BaseModel):
    client_id: str
    type: str
    message: str | None = None
    data: dict | None = None


@app.post("/logs")
async def collect_logs(event: LogEvent, request: Request):
    # Centralize client-side debug into server logs (no secrets)
    logger.info(
        "client.log %s",
        json.dumps(
            {
                "client_id": event.client_id,
                "evt_type": event.type,
                "evt_message": event.message,
                "evt_data": event.data,
                "remote": request.client.host if request.client else None,
            },
            ensure_ascii=False,
        ),
    )
    return {"ok": True}
