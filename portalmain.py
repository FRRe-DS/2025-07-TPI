import os, time, jwt, httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .dtos import *

app = FastAPI(title="Portal de Compras API", version="1.0.0")

# Config externa
STOCK_URL = os.getenv("STOCK_URL", "http://localhost:8001")
LOGI_URL  = os.getenv("LOGI_URL",  "http://localhost:8002")
JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
JWT_EXP_S  = int(os.getenv("JWT_EXP_S", "3600"))

auth = HTTPBearer()

# “DB” en memoria
USUARIOS: dict[str, dict] = {}    # email -> {"nombre","apellido","password"}
CARRITOS: dict[str, Cart] = {}    # email -> Cart
ORDENES:  dict[str, Order] = {}   # orderId -> Order

# ——— Helpers JWT ———
def issue_token(email: str) -> str:
    now = int(time.time())
    payload = {"sub": email, "iat": now, "exp": now + JWT_EXP_S}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def require_user(tok: HTTPAuthorizationCredentials = Depends(auth)) -> str:
    try:
        data = jwt.decode(tok.credentials, JWT_SECRET, algorithms=["HS256"])
        return data["sub"]
    except Exception:
        raise HTTPException(401, "Token inválido o expirado")

# ——— Auth ———
@app.post("/api/auth/register", status_code=201)
def register(body: AuthRegister):
    if body.password != body.confirmPassword:
        raise HTTPException(400, "Las contraseñas no coinciden")
    if body.email in USUARIOS:
        raise HTTPException(409, "Email ya registrado")
    USUARIOS[body.email] = {
        "nombre": body.nombre, "apellido": body.apellido, "password": body.password
    }
    return {"ok": True}

@app.post("/api/auth/login", response_model=TokenPair)
def login(body: AuthLogin):
    u = USUARIOS.get(body.email)
    if not u or u["password"] != body.password:
        raise HTTPException(401, "Credenciales inválidas")
    return TokenPair(accessToken=issue_token(body.email))

@app.get("/api/auth/refresh", response_model=TokenPair)
def refresh(user: str = Depends(require_user)):
    return TokenPair(accessToken=issue_token(user))

# ——— Productos (frontend a backend Compras) ———
@app.get("/api/product", response_model=list[Producto])
async def list_products():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{STOCK_URL}/api/product", timeout=10)
    if r.status_code != 200:
        raise HTTPException(502, "Stock no disponible")
    return r.json()

@app.get("/api/product/{pid}", response_model=Producto)
async def get_product(pid: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{STOCK_URL}/api/product/{pid}", timeout=10)
    if r.status_code == 404:
        raise HTTPException(404, "Producto no encontrado")
    if r.status_code != 200:
        raise HTTPException(502, "Stock no disponible")
    return r.json()

# ——— Carrito (CRUD) ———
@app.get("/api/shopcart", response_model=Cart)
def get_cart(user: str = Depends(require_user)):
    return CARRITOS.get(user, Cart())

@app.post("/api/shopcart", response_model=Cart)
def upsert_cart(item: CartItem, user: str = Depends(require_user)):
    cart = CARRITOS.get(user, Cart())
    # upsert
    for it in cart.items:
        if it.productId == item.productId:
            it.quantity = item.quantity
            break
    else:
        cart.items.append(item)
    CARRITOS[user] = cart
    return cart

@app.delete("/api/shopcart", response_model=Cart)
def clear_cart(user: str = Depends(require_user)):
    CARRITOS[user] = Cart()
    return CARRITOS[user]

# ——— Checkout / Historial ———
@app.post("/api/shopcart/checkout", status_code=201)
async def checkout(body: dict, user: str = Depends(require_user)):
    """
    body: {
      "direccionEntrega": { "calle": "...", "ciudad": "...", ... },
      "medioTransporte": "camion|tren|barco|avion"
    }
    """
    cart = CARRITOS.get(user)
    if not cart or not cart.items:
        raise HTTPException(400, "Carrito vacío")

    compra_id = f"C{len(ORDENES)+1}"
    booking_req = {
        "compraId": compra_id,
        "items": [{"productId": i.productId, "cantidad": i.quantity} for i in cart.items]
    }

    async with httpx.AsyncClient() as client:
        # 1) reservar en Stock
        r1 = await client.post(f"{STOCK_URL}/api/booking", json=booking_req, timeout=10)
        if r1.status_code not in (200, 201):
            raise HTTPException(r1.status_code, f"Reserva rechazada: {r1.text}")
        booking = r1.json()  # { bookingId, ... }

        # 2) crear tracking en Logística
        tracking_req = {
            "compraId": compra_id,
            "items": [{"productId": i.productId, "cantidad": i.quantity, "pesoKg": 0.5} for i in cart.items],
            "direccionEntrega": body["direccionEntrega"],
            "medioTransporte": body["medioTransporte"]
        }
        r2 = await client.post(f"{LOGI_URL}/api/tracking", json=tracking_req, timeout=10)
        if r2.status_code != 201:
            # deshacer reserva
            await client.post(f"{STOCK_URL}/api/booking/{booking['bookingId']}/release")
            raise HTTPException(r2.status_code, f"Logística falló: {r2.text}")
        tracking = r2.json()  # { trackingId }

        # 3) endpoints que “nosotros ofrecemos” para vincular
        await client.put(f"{STOCK_URL}/api/booking/{booking['bookingId']}",
                         json={"orderId": compra_id}, timeout=10)
        await client.put(f"{LOGI_URL}/api/tracking/{tracking['trackingId']}",
                         json={"orderId": compra_id}, timeout=10)

    # 4) persistencia local e higiene
    order = Order(id=compra_id, items=cart.items, status="reserved",
                  bookingId=booking["bookingId"], trackingId=tracking["trackingId"])
    ORDENES[order.id] = order
    CARRITOS[user] = Cart()
    return {"orderId": order.id, "bookingId": order.bookingId, "trackingId": order.trackingId}

@app.get("/api/shopcart/history", response_model=list[Order])
def list_orders(user: str = Depends(require_user)):
    # (si querés, filtrá por usuario; aquí lo dejamos simple)
    return list(ORDENES.values())

@app.get("/api/shopcart/history/{oid}", response_model=Order)
def get_order(oid: str, user: str = Depends(require_user)):
    o = ORDENES.get(oid)
    if not o: raise HTTPException(404, "Pedido no encontrado")
    return o

@app.delete("/api/shopcart/history/{oid}", status_code=204)
async def cancel_order(oid: str, user: str = Depends(require_user)):
    o = ORDENES.get(oid)
    if not o: raise HTTPException(404, "Pedido no encontrado")
    if o.status in ("shipped","delivered"):
        raise HTTPException(409, "No cancelable en este estado")

    async with httpx.AsyncClient() as client:
        if o.bookingId:
            await client.post(f"{STOCK_URL}/api/booking/{o.bookingId}/release", timeout=10)
        # (opcional) cancelar tracking en logística si definen endpoint
    o.status = "canceled"
    return
