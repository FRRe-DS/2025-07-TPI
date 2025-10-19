from rest_framework import generics, views, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .models import UserProfile, Cart, CartItem, Order, OrderItem
from .serializers import RegisterSerializer, UserProfileSerializer, CartSerializer, CartItemSerializer, OrderSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

import requests # Para llamar a otras APIs

# --- URLs de los otros servicios (¡cambia esto si es necesario!) ---
STOCK_SERVICE_URL = "https://api.stock.com/v1"
LOGISTICS_SERVICE_URL = "https://api.logistica.com/v1"


# --- Autenticación (Frontend - Auth) ---

class RegisterView(generics.CreateAPIView):
    # POST /api/auth/register
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

# Para /api/auth/login, podés usar la vista de SimpleJWT.
# La de /api/auth/refresh también la provee SimpleJWT.


# --- Perfil de Usuario (Frontend - Usuario) ---

class UserProfileView(views.APIView):
    # GET, POST, PUT /api/user/profile
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({"error": "Perfil no encontrado", "code": "PROFILE_NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            # Asocia el perfil al usuario logueado
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # ... (Implementar PUT de forma similar) ...


# --- Productos (Frontend - Productos) ---
# ¡Esta vista LLAMA a la API de Stock!

class ProductListView(views.APIView):
    # GET /api/product
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Llama al servicio de Stock para obtener productos
            response = requests.get(f"{STOCK_SERVICE_URL}/api/stock/product")
            
            if response.status_code == 200:
                return Response(response.json()) # Devuelve el JSON de la API de Stock
            
            return Response(
                {"error": "Servicio Stock no disponible", "code": "STOCK_SERVICE_UNAVAILABLE"},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except requests.exceptions.ConnectionError:
            return Response(
                {"error": "Servicio Stock no disponible", "code": "STOCK_SERVICE_UNAVAILABLE"},
                status=status.HTTP_502_BAD_GATEWAY
            )

class ProductDetailView(views.APIView):
    # GET /api/product/{id}
    permission_classes = [AllowAny]

    def get(self, request, id):
        try:
            response = requests.get(f"{STOCK_SERVICE_URL}/api/stock/product/{id}")
            
            if response.status_code == 200:
                return Response(response.json())
            elif response.status_code == 404:
                return Response(
                    {"error": "Producto no encontrado", "code": "PRODUCT_NOT_FOUND"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"error": "Servicio Stock no disponible", "code": "STOCK_SERVICE_UNAVAILABLE"},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except requests.exceptions.ConnectionError:
             return Response(
                {"error": "Servicio Stock no disponible", "code": "STOCK_SERVICE_UNAVAILABLE"},
                status=status.HTTP_502_BAD_GATEWAY
            )

# --- Carrito (Frontend - Carrito) ---

class CartView(views.APIView):
    # GET, POST, PUT, DELETE /api/shopcart
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtiene o crea un carrito para el usuario
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # ANTES de serializar, actualizamos los datos de los productos desde la API de Stock
        # (Esta parte es compleja: hay que iterar items, llamar a la API de Stock
        # para obtener precio/nombre/etc. y armar la respuesta como en 'Cart')
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        # POST /api/shopcart (Agregar al carrito)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        productId = request.data.get('productId')
        quantity = int(request.data.get('quantity', 1))

        # 1. TODO: Verificar que el producto existe en la API de Stock
        # 2. TODO: Verificar stock en la API de Stock
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            productId=productId
        )
        
        if not created:
            cart_item.quantity += quantity # Si ya existe, suma la cantidad
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        return Response({"message": "Producto agregado al carrito"}, status=status.HTTP_201_CREATED)
    
    # ... (Implementar PUT y DELETE para actualizar/vaciar carrito) ...


# --- Checkout (Frontend - Pedidos) ---
# ¡La vista más importante! Llama a Stock y Logística

class CheckoutView(views.APIView):
    # POST /api/shopcart/checkout
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response({"error": "Carrito vacío", "code": "EMPTY_CART"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Preparar datos para las APIs
        booking_products = []
        order_items_data = []
        total_pedido = 0

        # 2. Obtener precios de la API de Stock y calcular total
        for item in cart.items.all():
            try:
                # Consultar precio y stock del producto
                prod_response = requests.get(f"{STOCK_SERVICE_URL}/api/stock/product/{item.productId}")
                if prod_response.status_code != 200:
                    return Response({"error": f"Producto {item.productId} no encontrado"}, status=status.HTTP_404_NOT_FOUND)
                
                prod_data = prod_response.json()
                
                # Verificar stock (según 'openapi.yaml' la API de booking lo hace, pero podemos chequear)
                if prod_data['stock'] < item.quantity:
                     return Response({"error": f"Stock insuficiente para {prod_data['name']}", "code": "INSUFFICIENT_STOCK"}, status=status.HTTP_409_CONFLICT)

                # Armar la lista para reservar en Stock
                booking_products.append({"productId": item.productId, "quantity": item.quantity})
                
                # Armar la lista para guardar en nuestra Order
                price = float(prod_data['price'])
                order_items_data.append({
                    "productId": item.productId,
                    "quantity": item.quantity,
                    "price": price
                })
                total_pedido += (price * item.quantity)
                
            except requests.exceptions.ConnectionError:
                return Response({"error": "Servicio Stock no disponible", "code": "EXTERNAL_SERVICE_ERROR"}, status=status.HTTP_502_BAD_GATEWAY)

        # 3. Llamar a API de Stock para reservar productos
        try:
            booking_request_body = {"products": booking_products}
            booking_response = requests.post(f"{STOCK_SERVICE_URL}/api/stock/booking", json=booking_request_body)
            
            if booking_response.status_code != 201:
                return Response(booking_response.json(), status=booking_response.status_code) # Ej. 400 INSUFFICIENT_STOCK
            
            booking_data = booking_response.json()
            stock_booking_id = booking_data['id'] # Guardamos el ID de la reserva
            
        except requests.exceptions.ConnectionError:
            return Response({"error": "Servicio Stock no disponible", "code": "EXTERNAL_SERVICE_ERROR"}, status=status.HTTP_502_BAD_GATEWAY)

        # 4. Llamar a API de Logística para crear el envío
        try:
            tracking_request_body = {
                "orderId": None, # Aún no creamos nuestra orden, Logística debe permitirlo
                "address": request.data.get('deliveryAddress'),
                "products": booking_products # Lista de productos
            }
            tracking_response = requests.post(f"{LOGISTICS_SERVICE_URL}/api/logistics/tracking", json=tracking_request_body)

            if tracking_response.status_code != 201:
                # TODO: Idealmente, deberíamos cancelar la reserva de Stock si esto falla (transacción)
                return Response(tracking_response.json(), status=tracking_response.status_code)

            tracking_data = tracking_response.json()
            logistics_tracking_id = tracking_data['id'] # Guardamos el ID del tracking

        except requests.exceptions.ConnectionError:
            # TODO: Cancelar reserva de stock
            return Response({"error": "Servicio Logística no disponible", "code": "EXTERNAL_SERVICE_ERROR"}, status=status.HTTP_502_BAD_GATEWAY)

        # 5. Si todo salió bien, crear el Pedido (Order) en nuestra base de datos
        order_serializer = OrderSerializer(data={
            "user": request.user.id,
            "total": total_pedido,
            "status": "PROCESSING",
            "items": order_items_data,
        })
        
        if order_serializer.is_valid():
            order = order_serializer.save(
                user=request.user, 
                stock_booking_id=stock_booking_id, 
                logistics_tracking_id=logistics_tracking_id
            )
            
            # 6. TODO: Llamar a las APIs de Stock y Logística de nuevo para vincular
            # el ID de nuestro pedido (order.id) a la reserva y al tracking
            # PUT /api/booking/{id}  (Stock)
            # PUT /api/tracking/{id} (Logística)
            
            # 7. Vaciar el carrito
            cart.items.all().delete()
            
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        else:
            # TODO: Cancelar reserva y tracking
            return Response(order_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)