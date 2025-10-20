from fastapi import FastAPI, HTTPException
from typing import Dict
from logica import TrackingRequest, Tracking

app = FastAPI(title="Logística API", version="1.0.0")

TRACKS: Dict[str, Tracking] = {}  # trackingId -> Tracking

# ——— Ellos nos ofrecen ———
@app.post("/api/tracking", status_code=201)
def crear_tracking(req: TrackingRequest):
    tid = f"T{len(TRACKS)+1}"
    TRACKS[tid] = Tracking(trackingId=tid, pedidoId=None,
                           estado="pendiente", ubicacion="Centro de distribución")
    return {"trackingId": tid}

@app.get("/api/tracking/{id}", response_model=Tracking)
def obtener_tracking(id: str):
    t = TRACKS.get(id)
    if not t: raise HTTPException(404, "Tracking no encontrado")
    return t

# ——— Nosotros ofrecemos (Compras → Logística) ———
@app.put("/api/tracking/{id}")
def vincular_pedido_a_tracking(id: str, body: dict):
    """
    Body esperado: {"orderId": "..."}
    """
    t = TRACKS.get(id)
    if not t: raise HTTPException(404, "Tracking no encontrado")
    t.pedidoId = body.get("orderId")
    return {"status": "OK", "trackingId": id, "orderId": t.pedidoId}
