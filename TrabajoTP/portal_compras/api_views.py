from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import requests
from django.conf import settings
from .models import ShoppingCart, Order, OrderItem

@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    """
    Registro real de usuario + OAuth2 token
    Compatible con OAS: POST /api/auth/register
    """
    # Validar contraseñas
    if request.data.get('password') != request.data.get('confirmPassword'):
        return Response({
            'error': 'Las contraseñas no coinciden',
            'code': 'PASSWORD_MISMATCH'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificar si el usuario ya existe
    if User.objects.filter(email=request.data.get('email')).exists():
        return Response({
            'error': 'El email ya está registrado',
            'code': 'EMAIL_ALREADY_EXISTS'
        }, status=status.HTTP_409_CONFLICT)
    
    try:
        # Crear usuario
        user = User.objects.create_user(
            username=request.data['email'],
            email=request.data['email'],
            password=request.data['password'],
            first_name=request.data.get('firstName', ''),
            last_name=request.data.get('lastName', '')
        )
        
        # Obtener token OAuth2 para el nuevo usuario
        token_response = requests.post(
            f'http://{request.get_host()}/o/token/',
            data={
                'grant_type': 'password',
                'username': user.email,
                'password': request.data['password'],
                'client_id': settings.OAUTH2_CLIENT_ID  # Lo configuraremos
            }
        )
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            
            return Response({
                'message': 'Usuario registrado exitosamente',
                'accessToken': token_data['access_token'],
                'tokenType': token_data['token_type'],
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'firstName': user.first_name,
                    'lastName': user.last_name
                }
            }, status=status.HTTP_201_CREATED)
        else:
            # Si falla el token, igual creamos el usuario
            return Response({
                'message': 'Usuario registrado exitosamente. Por favor inicia sesión.',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'firstName': user.first_name,
                    'lastName': user.last_name
                }
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({
            'error': 'Error creando usuario',
            'code': 'USER_CREATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """
    Login real con OAuth2
    Compatible con OAS: POST /api/auth/login
    """
    try:
        # Obtener token OAuth2
        token_response = requests.post(
            f'http://{request.get_host()}/o/token/',
            data={
                'grant_type': 'password',
                'username': request.data.get('email'),
                'password': request.data.get('password'),
                'client_id': settings.OAUTH2_CLIENT_ID
            }
        )
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            
            # Obtener información del usuario
            user = User.objects.get(email=request.data.get('email'))
            
            return Response({
                'accessToken': token_data['access_token'],
                'tokenType': token_data['token_type'],
                'expiresIn': token_data['expires_in'],
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'firstName': user.first_name,
                    'lastName': user.last_name
                }
            })
        else:
            return Response({
                'error': 'Credenciales inválidas',
                'code': 'INVALID_CREDENTIALS'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except User.DoesNotExist:
        return Response({
            'error': 'Credenciales inválidas',
            'code': 'INVALID_CREDENTIALS'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({
            'error': 'Error en autenticación',
            'code': 'AUTH_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_api(request):
    """
    Perfil de usuario
    Compatible con OAS: GET /api/user/profile
    """
    user = request.user
    return Response({
        'id': user.id,
        'userId': user.id,
        'email': user.email,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'createdAt': user.date_joined.isoformat(),
        'updatedAt': user.last_login.isoformat() if user.last_login else user.date_joined.isoformat()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shopcart_get(request):
    """
    GET /api/shopcart - Ver carrito
    """
    cart, created = ShoppingCart.objects.get_or_create(user=request.user)
    
    # Formatear respuesta según OAS
    return Response({
        'items': cart.items,
        'total': cart.calculate_total()
    })

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def shopcart_update(request):
    """
    POST/PUT /api/shopcart - Agregar/actualizar item en carrito
    Body: {"productId": 1, "quantity": 2}
    """
    cart, created = ShoppingCart.objects.get_or_create(user=request.user)
    
    product_id = request.data.get('productId')
    quantity = request.data.get('quantity', 1)
    
    if not product_id:
        return Response({
            'error': 'productId es requerido',
            'code': 'PRODUCT_ID_REQUIRED'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # SOLO UNA VEZ - eliminar el duplicado
    productos_mock = {
        1: {'id': 1, 'name': 'Notebook Gamer', 'description': 'Laptop gaming', 'price': 1500.00, 'stock': 10, 'category': 'Tecnología'},
        2: {'id': 2, 'name': 'Mouse Inalámbrico', 'description': 'Mouse ergonómico', 'price': 45.99, 'stock': 25, 'category': 'Accesorios'},
        3: {'id': 3, 'name': 'Teclado Mecánico', 'description': 'Teclado gaming', 'price': 89.99, 'stock': 15, 'category': 'Accesorios'},
        4: {'id': 4, 'name': 'Monitor 24"', 'description': 'Monitor Full HD', 'price': 299.99, 'stock': 8, 'category': 'Tecnología'},
        5: {'id': 5, 'name': 'Auriculares Bluetooth', 'description': 'Auriculares inalámbricos', 'price': 129.99, 'stock': 20, 'category': 'Audio'}
    }
    
    producto_info = productos_mock.get(product_id, {
        'id': product_id,
        'name': f'Producto {product_id}',
        'description': f'Descripción del producto {product_id}',
        'price': 99.99,
        'stock': 10,
        'category': 'General'
    })
    
    # Buscar si el producto ya está en el carrito
    item_index = None
    for i, item in enumerate(cart.items):
        if item.get('productId') == product_id:
            item_index = i
            break
    
    if item_index is not None:
        # Actualizar cantidad existente
        cart.items[item_index]['quantity'] = quantity
    else:
        # Agregar nuevo item
        cart.items.append({
            'productId': product_id,
            'quantity': quantity,
            'product': producto_info
        })
    
    cart.save()
    cart.calculate_total()
    
    return Response({
        'message': 'Carrito actualizado',
        'items': cart.items,
        'total': cart.total
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def shopcart_clear(request):
    """
    DELETE /api/shopcart - Vaciar carrito
    """
    cart, created = ShoppingCart.objects.get_or_create(user=request.user)
    cart.items = []
    cart.total = 0
    cart.save()
    
    return Response({
        'message': 'Carrito vaciado'
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def shopcart_remove_item(request, productId):
    """
    DELETE /api/shopcart/{productId} - Remover producto del carrito
    """
    cart, created = ShoppingCart.objects.get_or_create(user=request.user)
    
    # Filtrar items, excluyendo el productId especificado
    cart.items = [item for item in cart.items if item.get('productId') != productId]
    cart.save()
    cart.calculate_total()
    
    return Response({
        'message': 'Producto removido del carrito',
        'items': cart.items,
        'total': cart.total
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_api(request):
    """
    POST /api/shopcart/checkout - Confirmar pedido
    """
    try:
        # 1. Obtener el carrito del usuario
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)
        
        if not cart.items:
            return Response({
                'error': 'Carrito vacío',
                'code': 'EMPTY_CART'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Validar datos requeridos
        delivery_address = request.data.get('deliveryAddress')
        payment_method = request.data.get('paymentMethod', 'credit_card')
        
        if not delivery_address:
            return Response({
                'error': 'Dirección de entrega requerida',
                'code': 'DELIVERY_ADDRESS_REQUIRED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 3. Crear la orden
        order = Order.objects.create(
            user=request.user,
            total=cart.total,
            delivery_address=delivery_address,
            payment_method=payment_method,
            status='PENDING'
        )
        
        # 4. Crear los items de la orden
        for cart_item in cart.items:
            OrderItem.objects.create(
                order=order,
                productId=cart_item['productId'],
                quantity=cart_item['quantity'],
                price=cart_item['product']['price']
            )
        
        # 5. Aquí integraríamos con servicios externos (Stock y Logística)
        # Por ahora simulamos la integración
        order.stock_booking_id = 1000 + order.id  # Simulación
        order.logistics_tracking_id = 2000 + order.id  # Simulación
        order.save()
        
        # 6. Vaciar el carrito
        cart.items = []
        cart.total = 0
        cart.save()
        
        # 7. Preparar respuesta según OAS
        order_data = {
            'id': order.id,
            'date': order.date.isoformat(),
            'status': order.status,
            'total': float(order.total),
            'items': [
                {
                    'productId': item.productId,
                    'quantity': item.quantity,
                    'product': {
                        'id': item.productId,
                        'name': f'Producto {item.productId}',  # En producción obtener del servicio Stock
                        'price': float(item.price)
                    }
                } for item in order.items.all()
            ]
        }
        
        return Response(order_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'Error al procesar el checkout',
            'code': 'CHECKOUT_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_history_api(request):
    """
    GET /api/shopcart/history - Historial de pedidos
    """
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'date': order.date.isoformat(),
            'status': order.status,
            'total': float(order.total),
            'items': [
                {
                    'productId': item.productId,
                    'quantity': item.quantity,
                    'product': {
                        'id': item.productId,
                        'name': f'Producto {item.productId}',
                        'price': float(item.price)
                    }
                } for item in order.items.all()
            ]
        })
    
    return Response(orders_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail_api(request, id):
    """
    GET /api/shopcart/history/{id} - Detalle de un pedido específico
    """
    try:
        order = Order.objects.prefetch_related('items').get(id=id, user=request.user)
        
        order_data = {
            'id': order.id,
            'date': order.date.isoformat(),
            'status': order.status,
            'total': float(order.total),
            'delivery_address': order.delivery_address,
            'payment_method': order.payment_method,
            'stock_booking_id': order.stock_booking_id,
            'logistics_tracking_id': order.logistics_tracking_id,
            'items': [
                {
                    'productId': item.productId,
                    'quantity': item.quantity,
                    'product': {
                        'id': item.productId,
                        'name': f'Producto {item.productId}',
                        'price': float(item.price)
                    }
                } for item in order.items.all()
            ]
        }
        
        return Response(order_data)
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Pedido no encontrado',
            'code': 'ORDER_NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_order_api(request, id):
    """
    DELETE /api/shopcart/history/{id} - Cancelar pedido
    """
    try:
        order = Order.objects.get(id=id, user=request.user)
        
        # Solo se pueden cancelar pedidos pendientes o en procesamiento
        if order.status not in ['PENDING', 'PROCESSING']:
            return Response({
                'error': 'No se puede cancelar un pedido ya enviado',
                'code': 'CANNOT_CANCEL_SHIPPED_ORDER'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'CANCELLED'
        order.save()
        
        return Response({
            'message': 'Pedido cancelado exitosamente'
        })
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Pedido no encontrado',
            'code': 'ORDER_NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)