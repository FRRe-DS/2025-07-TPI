from django.db import models

# Create your models here.

class Usuario (models.Model):
    Nombre = models.CharField(max_length=30)
    Apellido = models.CharField(max_length=30)
    Email = models.EmailField()
    Contraseña = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.Nombre} {self.Apellido}"
    
class Producto (models.Model):
    Nombre = models.CharField(max_length=50)
    Descripcion = models.TextField()
    Precio = models.DecimalField(max_digits=10, decimal_places=2)
    Stock = models.IntegerField()

    def __str__(self):
        return self.Nombre