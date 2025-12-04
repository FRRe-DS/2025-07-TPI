from django.db import models
from django.contrib.auth.models import User
from enum import Enum
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

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

class Order(models.Model):
    """Orden de compra"""
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PROCESSING', 'Procesando'),
        ('SHIPPED', 'Enviado'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    PAYMENT_METHODS = [
        ('credit_card', 'Tarjeta de Crédito'),
        ('debit_card', 'Tarjeta de Débito'),
        ('paypal', 'PayPal'),
        ('cash', 'Efectivo'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    delivery_address = models.TextField()
    payment_method = models.CharField(
        max_length=50, 
        choices=PAYMENT_METHODS, 
        default='credit_card'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING'
    )
    
    # IDs de integración con otros servicios
    stock_booking_id = models.CharField(max_length=100, null=True, blank=True)
    logistics_tracking_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Campos adicionales útiles
    customer_notes = models.TextField(blank=True, null=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-date']
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
    
    def __str__(self):
        return f"Orden #{self.id} - {self.user.email} - {self.get_status_display()}"
    
    def get_items(self):
        """Devuelve los items de la orden"""
        return self.items.all()
    
    def update_status(self, new_status):
        """Actualiza el estado de la orden"""
        if new_status in dict(self.STATUS_CHOICES):
            self.status = new_status
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    productId = models.IntegerField()  # <-- CON 'I' mayúscula
    product_name = models.CharField(max_length=255, default='')
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
    
    def __str__(self):
        return f"Producto {self.productId} x{self.quantity}"
    
    @property
    def subtotal(self):
        return self.price * Decimal(str(self.quantity))
    
    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = f"Producto {self.productId}"  # <-- También aquí
        super().save(*args, **kwargs)