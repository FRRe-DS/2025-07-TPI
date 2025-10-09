from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class Address(BaseModel):
    calle: str
    ciudad: str
    provincia: Optional[str] = None
    cp: Optional[str] = None
    pais: str = "AR"

class ItemEnvio(BaseModel):
    productId: str
    cantidad: int = Field(ge=1)
    pesoKg: float = Field(ge=0)

class TrackingRequest(BaseModel):
    compraId: str
    items: List[ItemEnvio]
    direccionEntrega: Address
    medioTransporte: str  

class Tracking(BaseModel):
    trackingId: str
    pedidoId: Optional[str] = None  # se completa al vincular
    estado: str  # pendiente, en_transito, entregado
    ubicacion: str
