from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token 
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
import httpx



# from .models import Usuario

# Create your views here.

def Inicio(request):
    return render(request, 'Compras/Inicio.html')

@api_view(['GET']) # <-- Esto le dice a DRF que esta vista es una API
def lista_productos(request):
    stock_url = "https://api.stock.com/v1/api/stock/product"
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


    # 2. Esta es la vista para registrar un usuario (POST /api/auth/register)
@api_view(['POST'])
def register_view(request):
    if request.method == 'POST':
        # 1. Pasa el JSON del request al serializador
        serializer = RegisterSerializer(data=request.data)
        
        # 2. Valida los datos (usando el método .validate() del serializador)
        if serializer.is_valid():
            # 3. Si es válido, llama al método .create() del serializador y guarda el usuario
            user = serializer.save()
            return Response({"message": f"Usuario '{user.username}' registrado exitosamente"}, status=status.HTTP_201_CREATED)
        else:
            # 4. Si no es válido, devuelve los errores
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        # 1. Pasamos los datos al serializador
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            # 2. Si los datos no son válidos (ej. falta 'username'), devuelve error
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 3. Datos validados, los extraemos
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # 4. ¡La autenticación!
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 5. Si el usuario es válido, creamos o recuperamos su token
            token, created = Token.objects.get_or_create(user=user)

            # 6. Devolvemos el token
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            }, status=status.HTTP_200_OK)
        else:
            # 7. Si el usuario no es válido (contraseña o user incorrecto)
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)