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

@api_view(['GET']) # <-- Esto le dice a DRF que esta vista es una API
def lista_productos(request):
    stock_url = "http://127.0.0.1:8082/productos"

    print(f"--- Intentando llamar a: {stock_url} ---")
    
    try:
        # 1. Usamos httpx para "llamar" al OTRO servicio
        response = httpx.get(stock_url)
        response.raise_for_status() # Lanza un error si la API de Stock falló
        
        # 2. Obtenemos los productos que nos dio Stock en formato JSON
        productos_json = response.json()
        
        # 3. Usamos 'Response' de DRF para devolver el JSON al frontend
        return Response(productos_json) 
        
    except httpx.RequestError as exc:
        # 4. Si la API de Stock se cayó, le avisamos al frontend
        error_msg = {"error": "El servicio de Stock no está disponible."}
        # 502 = "Bad Gateway", un error estándar para esto
        return Response(error_msg, status=502)


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
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)