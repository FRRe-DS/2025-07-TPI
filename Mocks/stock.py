from pydantic import BaseModel, Field
from typing import Optional, List, Dict

# —— Productos ——
class Dinero(BaseModel):
    amount: float = Field(ge=0)
    currency: str = "ARS"

class Producto(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str] = None
    precio: Dinero
    pesoKg: float = Field(ge=0)
    stock: int = Field(ge=0)
    imagen_url: Optional[str] = None

# —— Booking (reservas) ——
class ItemReserva(BaseModel):
    productId: str
    cantidad: int = Field(ge=1)

class BookingRequest(BaseModel):
    compraId: str
    items: List[ItemReserva]

class Booking(BaseModel):
    bookingId: str
    compraId: str
    items: Dict[str, int]  # productId -> cantidad
    estado: str  # reservado, liberado
