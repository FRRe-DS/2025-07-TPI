from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ShippingStatus(str, Enum):
    CREATED = "created"
    RESERVED = "reserved"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"
    IN_DISTRIBUTION = "in_distribution"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class TransportType(str, Enum):
    COURIER = "courier"
    PICKUP = "pickup"
    THIRD_PARTY = "third_party"

class Address(BaseModel):
    street: str
    number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class ProductQty(BaseModel):
    product_id: int
    quantity: int

class ShippingLog(BaseModel):
    timestamp: datetime
    status: ShippingStatus
    message: Optional[str] = None
    actor: Optional[str] = None

class ShippingDetail(BaseModel):
    shipping_id: int
    order_id: int
    user_id: int
    delivery_address: Address
    products: List[ProductQty] = Field(default_factory=list)
    status: ShippingStatus
    transport_type: TransportType
    estimated_delivery_at: datetime
    created_at: datetime
    updated_at: datetime
    logs: List[ShippingLog] = Field(default_factory=list)

    # Campos opcionales
    departure_address: Optional[Address] = None
    tracking_number: Optional[str] = None
    carrier_name: Optional[str] = None
    total_cost: Optional[float] = None
    currency: Optional[str] = None

    class Config:
        orm_mode = True
        use_enum_values = True
        allow_population_by_field_name = True
