from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from .config import API_KEY
from orchestrator.orchestrator import handle_request

app = FastAPI()


@app.post("/honeypot")
async def honeypot(request: Request):
    if request.headers.get("content-type") != "application/json":
        raise HTTPException(status_code=400, detail="Invalid content type")

    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    try:
        result = handle_request(payload)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
@app.get("/health")
async def health_check():
    return {"status": "ok"}

