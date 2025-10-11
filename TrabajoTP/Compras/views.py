from django.shortcuts import render
from django.http import HttpResponse
from .models import Producto, Usuario

# Create your views here.

def Inicio(request):
    return render(request, 'Compras/Inicio.html')

def crear_Producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')

        producto = Producto(Nombre=nombre, Descripcion=descripcion, Precio=precio, Stock=stock)
        producto.save()
        return HttpResponse("Producto creado exitosamente.")
    return render(request, 'Compras/crear_producto.html')