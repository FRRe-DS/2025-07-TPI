from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token 
from django.contrib.auth.models import User
from rest_framework.views import APIView
from .serializers import RegisterSerializer, LoginSerializer

from rest_framework.response import Response
from rest_framework import status, generics
import httpx



# from .models import Usuario

# Create your views here.

def Inicio(request):
    return render(request, 'Compras/Inicio.html')

@api_view(['GET'])
def lista_productos(request):
    
    # Esta es la URL del mock de Stock (main.py)
    stock_url = "http://127.0.0.1:8001/api/product" 
    
    print(f"--- [Django] Intentando llamar a: {stock_url} ---")

    try:
        # 1. Llamada simple, sin tokens
        response = httpx.get(stock_url)
        response.raise_for_status() # Lanza un error si la API de Stock falla
        
        productos_json = response.json()
        print("--- [Django] ¡Llamada exitosa! Productos recibidos de Stock. ---")
        
        # 2. Devuelve los productos al frontend
        return Response(productos_json) 
        
    except httpx.HTTPStatusError as exc:
        # Captura errores 4xx y 5xx del mock de Stock
        print(f"--- [Django] ERROR: El mock de Stock devolvió: {exc.response.status_code} ---")
        return Response(
            {"error": f"Error al conectar con Stock: {exc.response.status_code}"}, 
            status=exc.response.status_code
        )
    except httpx.RequestError as exc:
        # Captura el error si el mock de Stock está apagado
        print(f"--- [Django] ERROR: No se pudo conectar al mock de Stock. ¿Está apagado? ---")
        error_msg = {"error": "El servicio de Stock no está disponible."}
        return Response(error_msg, status=502) # 502 Bad Gateway


class ProductDetailView(APIView):
    """
    Vista de API para obtener los detalles de un producto específico desde el servicio de Stock.
    Corresponde a GET /api/product/{id}
    """
    def get(self, request, pk, *args, **kwargs):
        # La URL del mock de Stock para un producto específico
        stock_url = f"http://127.0.0.1:8001/api/product/{pk}"
        
        print(f"--- [Django] Intentando llamar a: {stock_url} para producto {pk} ---")

        try:
            response = httpx.get(stock_url)
            response.raise_for_status() # Lanza un error si la API de Stock falla
            
            producto_json = response.json()
            print(f"--- [Django] ¡Llamada exitosa! Producto {pk} recibido de Stock. ---")
            
            return Response(producto_json)
            
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return Response(
                    {"error": "Producto no encontrado", "code": "PRODUCT_NOT_FOUND"},
                    status=status.HTTP_404_NOT_FOUND
                )
            print(f"--- [Django] ERROR: El mock de Stock devolvió: {exc.response.status_code} ---")
            return Response(
                {"error": f"Error al conectar con Stock: {exc.response.status_code}", "code": "STOCK_SERVICE_ERROR"},
                status=status.HTTP_502_BAD_GATEWAY # O 500, dependiendo del error específico
            )
        except httpx.RequestError as exc:
            print(f"--- [Django] ERROR: No se pudo conectar al mock de Stock para producto {pk}. ¿Está apagado? ---")
            error_msg = {"error": "El servicio de Stock no está disponible.", "code": "STOCK_SERVICE_UNAVAILABLE"}
            return Response(error_msg, status=status.HTTP_502_BAD_GATEWAY)

class RegisterView(generics.CreateAPIView):
    """
    Vista de API para registrar un nuevo usuario.
    Al ser una CreateAPIView, automáticamente maneja POST para crear
    y GET para mostrar un formulario en la API Navegable.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class LoginView(APIView):
    """
    Vista de API para el login de usuarios.
    """
    # Le dice a la API Navegable qué formulario mostrar
    serializer_class = LoginSerializer 

    def get(self, request, *args, **kwargs):
        """
        Maneja GET para mostrar el formulario de login en la API Navegable.
        (Esto arregla el error "GET no permitido" de la Imagen 2)
        """
        # Simplemente devolvemos una respuesta vacía, 
        # DRF usará 'serializer_class' para renderizar el formulario.
        return Response()

    def post(self, request, *args, **kwargs):
        """
        Maneja POST para autenticar al usuario.
        """

        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Buscamos al usuario por su email
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            user_obj = None

        if user_obj:
            # Usamos el username encontrado para autenticar
            user = authenticate(request, username=user_obj.username, password=password)
        
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)