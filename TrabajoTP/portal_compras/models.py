from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20)
    dni = models.CharField(max_length=15)
    birthDate = models.DateField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class ShoppingCart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)  # ✅ Un carrito por usuario
    items = models.JSONField(default=list)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)     
    
    class Meta:
        db_table = 'shopping_carts' 
    
    def __str__(self):
        return f"Shopping cart of {self.user.username}"
    
    def calculate_total(self): 
        total = 0
        for item in self.items:
            price = item.get('product', {}).get('price', 0) if item.get('product') else 0
            total += item.get('quantity', 0) * price
        self.total = total
        self.save()
        return total

# Modelo para los Pedidos
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PROCESSING', 'Procesando'),
        ('SHIPPED', 'Enviado'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Múltiples órdenes por usuario
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Información de envío y pago (agregar estos campos)
    delivery_address = models.TextField()
    payment_method = models.CharField(max_length=50, default='credit_card')
    
    # IDs de los servicios externos
    stock_booking_id = models.CharField(max_length=100, null=True, blank=True)
    logistics_tracking_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.user.username} - {self.status}"

    class Meta:
        ordering = ['-date']  # Ordenar por fecha descendente

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    productId = models.IntegerField()
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Aquí sí guardamos el precio