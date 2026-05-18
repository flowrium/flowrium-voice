"""Flowrium Voice - STT Gateway Service

Proxies audio to FunASR Docker service (ws://localhost:10095).
No ML dependencies needed — this is a pure gateway.

Quick prototype for validating:
- FunASR Chinese/English/mixed transcription quality
- Real-time streaming latency
- CPU server performance
- Office noise robustness
"""

import asyncio
import json
import logging
import tempfile
from pathlib import Path

import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger("flowrium-voice")

FUNASR_WS_URL = "ws://localhost:10095"

app = FastAPI(title="Flowrium Voice STT", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    try:
        async with websockets.connect(FUNASR_WS_URL, close_timeout=2) as ws:
            await ws.close()
        funasr_status = "ok"
    except Exception:
        funasr_status = "unreachable"
    return {"status": "ok", "funasr": funasr_status, "url": FUNASR_WS_URL}


# ── Real-time streaming: proxy to FunASR ────────────────────


@app.websocket("/ws/stream")
async def ws_stream(websocket: WebSocket):
    await websocket.accept()

    try:
        async with websockets.connect(FUNASR_WS_URL) as funasr_ws:
            # Send initial config to FunASR
            config = {
                "mode": "2pass",
                "chunk_size": [5, 10, 5],
                "wav_name": "microphone",
                "is_speaking": True,
                "wav_format": "pcm",
                "audio_fs": 16000,
            }
            await funasr_ws.send(json.dumps(config))
            logger.info("Connected to FunASR, config sent")

            async def forward_to_funasr():
                """Forward audio from browser to FunASR."""
                try:
                    while True:
                        msg = await websocket.receive()

                        if msg["type"] == "websocket.disconnect":
                            await funasr_ws.send(json.dumps({"is_speaking": False}))
                            break

                        if msg.get("bytes"):
                            await funasr_ws.send(msg["bytes"])

                        if msg.get("text"):
                            try:
                                data = json.loads(msg["text"])
                                if data.get("type") == "stop":
                                    await funasr_ws.send(json.dumps({"is_speaking": False}))
                                    break
                            except json.JSONDecodeError:
                                pass
                except WebSocketDisconnect:
                    await funasr_ws.send(json.dumps({"is_speaking": False}))
                except Exception as e:
                    logger.error(f"Forward to FunASR error: {e}")

            async def forward_to_client():
                """Forward results from FunASR to browser."""
                try:
                    async for raw in funasr_ws:
                        result = json.loads(raw)
                        text = result.get("text", "")
                        is_final = result.get("is_final", False)
                        mode = result.get("mode", "")

                        msg_type = "final" if is_final or "offline" in mode else "partial"
                        await websocket.send_json({"type": msg_type, "text": text})
                except websockets.ConnectionClosed:
                    pass
                except Exception as e:
                    logger.error(f"Forward to client error: {e}")

            await asyncio.gather(
                forward_to_funasr(),
                forward_to_client(),
            )

    except Exception as e:
        logger.error(f"FunASR connection error: {e}")
        try:
            await websocket.send_json({"type": "error", "text": f"FunASR connection failed: {e}"})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


# ── Offline transcription: send file to FunASR ──────────────


@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    suffix = Path(file.filename or "audio.wav").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # Read audio file as bytes and send to FunASR via WebSocket
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()

        text = await _transcribe_via_funasr(audio_bytes)
        return {"text": text}
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        Path(tmp_path).unlink(missing_ok=True)


async def _transcribe_via_funasr(audio_bytes: bytes) -> str:
    """Send audio to FunASR and collect the final result."""
    async with websockets.connect(FUNASR_WS_URL) as ws:
        config = {
            "mode": "offline",
            "wav_name": "upload",
            "is_speaking": True,
            "wav_format": "wav",
            "audio_fs": 16000,
        }
        await ws.send(json.dumps(config))
        await ws.send(audio_bytes)
        await ws.send(json.dumps({"is_speaking": False}))

        final_text = ""
        async for raw in ws:
            result = json.loads(raw)
            text = result.get("text", "")
            is_final = result.get("is_final", False)
            if text:
                final_text = text
            if is_final:
                break

    return final_text


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
