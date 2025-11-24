from fastapi import FastAPI, HTTPException
from typing import Dict
from Stock import Producto, Dinero, BookingRequest, Booking

app = FastAPI(title="Stock API", version="1.0.0")

# “DB” en memoria
PRODUCTOS: Dict[str, Producto] = {
    "P1": Producto(id="P1", nombre="Notebook 14", descripcion="8GB/256GB",
                   precio=Dinero(amount=499999), pesoKg=1.4, stock=5),
    "P2": Producto(id="P2", nombre="Mouse USB", descripcion="Óptico",
                   precio=Dinero(amount=8999), pesoKg=0.2, stock=25),
}
BOOKINGS: Dict[str, Booking] = {}      # bookingId -> Booking
POR_COMPRA: Dict[str, str] = {}        # compraId  -> bookingId

# ——— Ellos nos ofrecen ———
@app.get("/api/product", response_model=list[Producto])
def listar_productos():
    return list(PRODUCTOS.values())

@app.get("/api/product/{id}", response_model=Producto)
def obtener_producto(id: str):
    p = PRODUCTOS.get(id)
    if not p: raise HTTPException(404, "Producto no encontrado")
    return p

@app.post("/api/booking", status_code=201, response_model=Booking)
def crear_booking(req: BookingRequest):
    # Validar stock
    for it in req.items:
        p = PRODUCTOS.get(it.productId)
        if not p or p.stock < it.cantidad:
            raise HTTPException(409, f"Sin stock para {it.productId}")
    # Descontar stock
    for it in req.items:
        PRODUCTOS[it.productId].stock -= it.cantidad

    booking_id = f"B{len(BOOKINGS)+1}"
    b = Booking(bookingId=booking_id,
                compraId=req.compraId,
                items={i.productId: i.cantidad for i in req.items},
                estado="reservado")
    BOOKINGS[booking_id] = b
    POR_COMPRA[req.compraId] = booking_id
    return b

@app.get("/api/booking/{id}", response_model=Booking)
def obtener_booking(id: str):
    b = BOOKINGS.get(id)
    if not b: raise HTTPException(404, "Booking no encontrado")
    return b

# ——— Nosotros ofrecemos (Compras → Stock) ———
@app.put("/api/booking/{id}")
def vincular_pedido_a_booking(id: str, body: dict):
    """
    Body esperado: {"orderId": "..."}  # para trazabilidad
    """
    b = BOOKINGS.get(id)
    if not b: raise HTTPException(404, "Booking no encontrado")
    # (acá podrías guardar relación orderId↔bookingId si querés)
    return {"status": "OK", "bookingId": id, "orderId": body.get("orderId")}

# Auxiliar para liberar si falla logística o cancelan
@app.post("/api/booking/{id}/release")
def liberar_booking(id: str):
    b = BOOKINGS.get(id)
    if not b or b.estado == "liberado":
        return {"status": "NO-OP"}
    # devolver stock
    for pid, cant in b.items.items():
        if pid in PRODUCTOS:
            PRODUCTOS[pid].stock += cant
    b.estado = "liberado"
    return {"status": "LIBERADO", "bookingId": id}
