from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict

# — Auth —
class AuthRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    confirmPassword: str
    nombre: str
    apellido: str

class AuthLogin(BaseModel):
    email: EmailStr
    password: str

class TokenPair(BaseModel):
    accessToken: str
    tokenType: str = "Bearer"

# — Productos (como los entrega Stock) —
class Dinero(BaseModel):
    amount: float
    currency: str = "ARS"

class Producto(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str] = None
    precio: Dinero
    pesoKg: float

# — Carrito / Pedidos —
class CartItem(BaseModel):
    productId: str
    quantity: int = Field(ge=1)

class Cart(BaseModel):
    items: List[CartItem] = []

class Order(BaseModel):
    id: str
    items: List[CartItem]
    status: str  # created, reserved, shipped, delivered, canceled
    bookingId: Optional[str] = None
    trackingId: Optional[str] = None
