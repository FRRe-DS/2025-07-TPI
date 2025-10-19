from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# En Compras/models.py
from django.db import models
# 1. IMPORTA EL MODELO 'USER' DE DJANGO
from django.contrib.auth.models import User as Usuario


# 3. CREA LOS MODELOS Y CONÉCTALOS AL 'USER' DE DJANGO

class Carrito(models.Model):
    """
    Un modelo para el carrito de compras de un usuario.
    """
    # Se conecta 1-a-1 con el Usuario de Django
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='carrito')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}" # 🛒

class ItemCarrito(models.Model):
    """
    Un item (producto) específico dentro de un carrito.
    """
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    
    # Este es el ID del producto que vive en la API de "Stock"
    producto_id = models.IntegerField() 
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x (Producto ID: {self.producto_id})"

class Pedido(models.Model):
    """
    Un pedido confirmado por un usuario.
    """
    # Se conecta con el Usuario de Django (un usuario puede tener muchos pedidos)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='pedidos')
    estado = models.CharField(max_length=50, default='Pendiente')
    direccion_entrega = models.CharField(max_length=255)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    # El ID de tracking que nos dará la API de "Logística"
    tracking_id_logistica = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Pedido {self.id} de {self.usuario.username}" # 📦

class ItemPedido(models.Model):
    """
    Los items específicos que se incluyeron en un pedido.
    """
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto_id = models.IntegerField()
    cantidad = models.PositiveIntegerField()
    # Guardamos el precio del momento de la compra
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)










'''
class Usuario (models.Model):
    Nombre = models.CharField(max_length=30)
    Apellido = models.CharField(max_length=30)
    Email = models.EmailField()
    Contraseña = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.Nombre} {self.Apellido}"
'''
