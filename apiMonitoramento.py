from fastapi import FastAPI, Request
from typing import Dict
import time

app = FastAPI()
dados_maquinas: Dict[str, Dict] = {}

@app.post("/status")
async def receber_status(request: Request):
    json_data = await request.json()
    hostname = json_data.get("hostname", f"sem_nome_{(int(time.time()))}")
    json_data["timestamp"] = time.time()
    dados_maquinas[hostname] = json_data
    return {"status": "ok"}

@app.get("/dashboard")
def mostrar_dashboard():
    return dados_maquinas