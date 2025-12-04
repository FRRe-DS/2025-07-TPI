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
    
    # ✅ ACTUALIZAR INFORMACIÓN DE PRODUCTOS CON DATOS REALES
    try:
        cart_updated = False
        for item in cart.items:
            product_id = item.get('productId')
            current_product = item.get('product', {})
            
            # Si el producto tiene nombre mockeado, actualizar
            if current_product and ('Producto' in current_product.get('name', '') or current_product.get('name', '').startswith('Producto ')):
                producto_real = obtener_producto_real(request, product_id)
                if producto_real:
                    item['product'] = producto_real
                    cart_updated = True
        
        if cart_updated:
            cart.save()
            
    except Exception as e:
        print(f"Error actualizando carrito: {e}")
    
    # Formatear respuesta según OAS
    return Response({
        'items': cart.items,
        'total': cart.calculate_total()
    })

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def shopcart_update(request):
    """
    POST/PUT /api/shopcart/items/ - Agregar/actualizar item en carrito
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
    
    # ✅ CONSULTAR API EXTERNA DE STOCK - REEMPLAZAR MOCK
    producto_info = obtener_producto_real(request, product_id)
    
    if not producto_info:
        return Response({
            'error': 'Producto no encontrado',
            'code': 'PRODUCT_NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)
    
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
        # Agregar nuevo item con información REAL
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

# ✅ AGREGAR FUNCIÓN PARA OBTENER PRODUCTO REAL
def obtener_producto_real(request, product_id):
    """
    Obtener información real del producto desde la API de Stock
    """
    try:
        # Obtener token del usuario autenticado
        social_auth = request.user.social_auth.get(provider='keycloak')
        access_token = social_auth.extra_data['access_token']
        
        # Consultar API de Stock
        stock_url = f"{settings.STOCK_API_URL}/productos/{product_id}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(stock_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            producto_data = response.json()
            
            # Transformar a formato compatible con el carrito
            categoria_principal = 'General'
            if producto_data.get('categorias') and len(producto_data['categorias']) > 0:
                categoria_principal = producto_data['categorias'][0].get('nombre', 'General')
            
            imagen_principal = None
            if producto_data.get('imagenes') and len(producto_data['imagenes']) > 0:
                for img in producto_data['imagenes']:
                    if img.get('esPrincipal'):
                        imagen_principal = img.get('url')
                        break
                if not imagen_principal:
                    imagen_principal = producto_data['imagenes'][0].get('url')
            
            return {
                'id': producto_data.get('id'),
                'name': producto_data.get('nombre'),
                'description': producto_data.get('descripcion'),
                'price': float(producto_data.get('precio', 0)),
                'stock': producto_data.get('stockDisponible', 0),
                'category': categoria_principal,
                'imagen_url': imagen_principal
            }
        else:
            print(f"❌ Error API Stock: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error obteniendo producto real: {e}")
        return None

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

def actualizar_productos_carrito(cart):
    """
    Actualizar información de productos en el carrito con datos reales de Stock
    """
    try:
        for item in cart.items:
            product_id = item.get('productId')
            
            # Si el producto tiene información mockeada o desactualizada
            if item.get('product') and ('Producto' in item['product'].get('name', '') or item['product'].get('name', '').startswith('Producto ')):
                
                # Obtener información real (necesitarías pasar el request o manejar el token de otra forma)
                # Para simplificar, podrías hacer esto al cargar el carrito
                pass
                
    except Exception as e:
        print(f"Error actualizando productos del carrito: {e}")

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

from django.utils import timezone

# portal_compras/api_views.py - Modifica checkout_api
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_api(request):
    """POST /api/shopcart/checkout - Confirmar pedido CON RESERVA EN STOCK Y ENVÍO EN LOGÍSTICA"""
    print(f"🔔 CHECKOUT INICIADO - Usuario: {request.user.username}")
    
    try:
        from datetime import datetime
        
        # 1. Obtener el carrito del usuario
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)
        print(f"🛒 Carrito obtenido: {len(cart.items)} items")
        
        if not cart.items:
            print("❌ Carrito vacío")
            return Response({
                'error': 'Carrito vacío',
                'code': 'EMPTY_CART'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Validar datos requeridos
        delivery_address = request.data.get('deliveryAddress')
        payment_method = request.data.get('paymentMethod', 'credit_card')
        ciudad = request.data.get('ciudad', '')
        provincia = request.data.get('provincia', '')
        codigo_postal = request.data.get('codigoPostal', '')
        
        if not delivery_address:
            print("❌ Dirección faltante")
            return Response({
                'error': 'Dirección de entrega requerida',
                'code': 'DELIVERY_ADDRESS_REQUIRED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 3. ✅ CREAR RESERVA EN STOCK
        print("🔄 Creando reserva en Stock...")
        reserva_resultado = crear_reserva_stock(request, cart.items, delivery_address)
        
        if not reserva_resultado.get('success'):
            error_msg = reserva_resultado.get('error', 'Error al crear reserva en Stock')
            print(f"❌ Error en reserva: {error_msg}")
            return Response({
                'error': error_msg,
                'code': 'STOCK_RESERVATION_FAILED',
                'details': reserva_resultado.get('details')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"✅ Reserva creada en Stock: {reserva_resultado.get('reserva_id')}")
        
        # 4. Crear la orden en nuestra base de datos
        total = sum(
            (item.get('cantidad', 0) * item.get('producto', {}).get('price', 0)) or 
            (item.get('quantity', 0) * item.get('product', {}).get('price', 0))
            for item in cart.items
        )
        print(f"💰 Total calculado: {total}")
        
        order = Order.objects.create(
            user=request.user,
            total=total,
            delivery_address=delivery_address,
            payment_method=payment_method,
            status='PENDING',
            stock_booking_id=reserva_resultado.get('reserva_id')
        )
        print(f"✅ Orden creada en DB: #{order.id}")
        
        # 5. Crear los items de la orden
        for cart_item in cart.items:
            precio = (
                cart_item.get('producto', {}).get('price') or 
                cart_item.get('product', {}).get('price') or 
                0
            )
            
            OrderItem.objects.create(
                order=order,
                productId=cart_item.get('producto_id') or cart_item.get('productId'),
                quantity=cart_item.get('cantidad') or cart_item.get('quantity', 1),
                price=precio
            )
        print(f"✅ Items de orden creados: {len(cart.items)}")
        
        # 6. ✅ EXTRACCÍON DE PRODUCTOS DE LA RESERVA PARA LOGÍSTICA
        print("📦 Extrayendo productos de la reserva para Logística...")
        productos_envio = []

        # Verificar que tenemos datos de la reserva
        if reserva_resultado.get('success') and 'data' in reserva_resultado:
            reserva_data = reserva_resultado['data']
            
            if 'items' in reserva_data and reserva_data['items']:
                print(f"🔍 Encontrados {len(reserva_data['items'])} items en la reserva")
                
                for item in reserva_data['items']:
                    print(f"📋 Procesando item: {item.get('nombre')}")
                    
                    # Extraer datos del producto
                    producto_id = item.get('productoId')
                    nombre = item.get('nombre', f'Producto {producto_id}')
                    cantidad = item.get('cantidad', 1)
                    
                    # El peso está dentro de item['producto']
                    producto_info = item.get('producto', {})
                    peso_kg = producto_info.get('pesoKg', '0.5')
                    
                    # También podemos extraer dimensiones si las necesita Logística
                    dimensiones = producto_info.get('dimensiones', {})
                    
                    productos_envio.append({
                        'producto_id': producto_id,
                        'nombre': nombre,
                        'cantidad': cantidad,
                        'precio_unitario': item.get('precioUnitario', '0'),
                        'peso_kg': peso_kg,
                        'dimensiones': dimensiones,
                        'ubicacion': producto_info.get('ubicacion', {})
                    })
                    
                    print(f"   ✅ Item extraído: {nombre}, cantidad: {cantidad}, peso: {peso_kg}kg")
            else:
                print("⚠️ No hay items en la reserva o estructura incorrecta")
        else:
            print("⚠️ No se pudo obtener datos de la reserva")

        print(f"📦 Total productos extraídos: {len(productos_envio)}")
        
        # 7. ✅ CREAR ENVÍO EN LOGÍSTICA
        print("🚚 Creando envío en Logística...")
        
        # Si no hay datos de ciudad/provincia, usar valores por defecto
        if not ciudad or not provincia:
            print("⚠️ Datos de ubicación incompletos, usando valores por defecto")
            ciudad = ciudad or "Ciudad"
            provincia = provincia or "Provincia"

        # Preparar datos para Logística CON LOS PRODUCTOS EXTRÍDOS
        envio_data = {
            'orden_id': order.id,  # ← AHORA order SÍ está definido
            'direccion_entrega': delivery_address,
            'ciudad': ciudad,
            'provincia': provincia,
            'codigo_postal': codigo_postal,
            'telefono': request.data.get('telefono', ''),
            'instrucciones': request.data.get('instrucciones', ''),
            'productos': productos_envio  # ← CON DATOS REALES
        }

        print(f"📝 Envio_data preparado con {len(productos_envio)} productos para orden #{order.id}")

        # Llamar a la función interna para crear el envío
        envio_resultado = None
        try:
            envio_resultado = crear_envio_logistica_interno(request, envio_data)
            
            if envio_resultado and envio_resultado.get('success'):
                shipping_id = envio_resultado.get('shipping_id')
                order.logistics_tracking_id = envio_resultado.get('shipping_id')
                order.save()
                print(f"✅ Envío creado en Logística: {order.logistics_tracking_id}")
            else:
                error_msg = envio_resultado.get('error', 'Error desconocido') if envio_resultado else 'No se pudo crear envío'
                print(f"⚠️ No se pudo crear envío en Logística: {error_msg}")
                # Continuamos aunque falle el envío
        except Exception as e:
            print(f"⚠️ Error al crear envío: {e}")
            # No fallamos el checkout completo si falla Logística
        
        # 8. Vaciar el carrito
        cart.items = []
        cart.total = 0
        cart.save()
        print("✅ Carrito vaciado")
        
        # 9. Preparar respuesta
        order_data = {
            'id': order.id,
            'date': order.date.isoformat(),
            'status': order.status,
            'total': float(order.total),
            'delivery_address': order.delivery_address,
            'payment_method': order.payment_method,
            'stock_booking_id': order.stock_booking_id,
            'compra_id': reserva_resultado.get('compra_id'),
            'reserva_estado': reserva_resultado.get('estado'),
            'message': 'Orden creada exitosamente'
        }
        
        # Solo agregar datos de logística si se creó exitosamente
        if envio_resultado and envio_resultado.get('success'):
            order_data['logistics_tracking_id'] = envio_resultado.get('tracking_id')
            order_data['envio_creado'] = True
        else:
            order_data['logistics_tracking_id'] = None
            order_data['envio_creado'] = False
            order_data['envio_error'] = envio_resultado.get('error', 'No se pudo crear envío') if envio_resultado else 'Error al crear envío'
        
        print(f"🎉 CHECKOUT COMPLETADO - Orden #{order.id}")
        
        return Response(order_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"💥 ERROR EN CHECKOUT: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': f'Error al procesar el checkout: {str(e)}',
            'code': 'CHECKOUT_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# En api_views.py - REEMPLAZA la función crear_envio_logistica_interno con esta versión

def crear_envio_logistica_interno(request, envio_data):
    print("="*60)
    print("🚚 DEBUG: Verificando settings...")
    
    LOGI_API_URL = getattr(settings, 'LOGI_API_URL', None)
    LOGI_API_CLIENT_ID = getattr(settings, 'LOGI_API_CLIENT_ID', None)
    
    print(f"🌐 LOGI_API_URL: {LOGI_API_URL}")
    print(f"🔑 LOGI_API_CLIENT_ID: {LOGI_API_CLIENT_ID}")
    
    try:
        # Obtener token
        print("🔐 Obteniendo token específico para Logística...")
        token = obtener_token_logistica_client_credentials()
        
        if not token:
            print("❌ No se pudo obtener token para Logística")
            return {
                'success': False,
                'error': 'No se pudo autenticar con el servicio de logística'
            }
        
        print(f"🔐 Token Client Credentials obtenido: {token[:30]}...")
        
        # Configurar headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # ✅ PREPARAR DATOS SEGÚN DOCUMENTACIÓN
        # 1. Products array (con "id", no "productId")
        products = []
        for producto in envio_data.get('productos', []):
            products.append({
                "id": int(producto.get('producto_id')),  # ← NÚMERO, se llama "id"
                "quantity": int(producto.get('cantidad', 1))  # ← NÚMERO
            })
        
        # Si no hay productos, usar datos por defecto
        if not products:
            products = [{
                "id": 1,
                "quantity": 1
            }]
        
        # 2. Delivery address (objeto estructurado)
        delivery_address = {
            "street": envio_data.get('direccion_entrega', ''),
            "city": envio_data.get('ciudad', 'Ciudad'),
            "state": envio_data.get('provincia', 'Provincia'),
            "postal_code": envio_data.get('codigo_postal', '') or "H3500ABC",
            "country": "AR"  # Argentina por defecto
        }
        
        # 3. Datos principales según documentación
        data_corregido = {
            "order_id": int(envio_data.get('orden_id', 0)),  # ← NÚMERO
            "user_id": int(request.user.id),  # ← NÚMERO
            "delivery_address": delivery_address,
            "transport_type": "road",  # ← REQUERIDO
            "products": products
        }
        
        print(f"📝 Datos CORREGIDOS según documentación: {data_corregido}")
        
        url = f"{LOGI_API_URL.rstrip('/')}/shipping"
        print(f"🔗 URL final: {url}")
        print(f"⏱️  Enviando POST a API de Logística...")
        
        response = requests.post(url, json=data_corregido, headers=headers, timeout=5)
        
        print(f"📡 RESPUESTA API LOGÍSTICA:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Contenido: {response.text[:500]}...")
        
        if response.status_code in [200, 201]:
            envio_response = response.json()
            print(f"✅ ÉXITO - Envío creado: {envio_response}")
            shipping_id = envio_response.get('shipping_id')
            return {
                'success': True,
                'tracking_id': shipping_id,
                'message': 'Envío creado exitosamente',
                'data': envio_response
            }
        else:
            print(f"❌ ERROR API Logística: {response.status_code}")
            print(f"❌ Detalles: {response.text}")
            return {
                'success': False,
                'error': f'Error del servicio Logística: {response.status_code}',
                'details': response.text
            }
            
    except Exception as e:
        print(f"💥 ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f'Error interno: {str(e)}'
        }
    finally:
        print("=" * 60)
# ✅ FUNCIÓN PARA RESERVAR PRODUCTOS EN STOCK
def reservar_productos_stock(request, items):
    """
    Integración con el servicio Stock para reservar productos
    """
    try:
        # Obtener token del usuario
        social_auth = request.user.social_auth.get(provider='keycloak')
        access_token = social_auth.extra_data['access_token']
        
        # Preparar datos para la reserva
        reserva_data = {
            'items': [
                {
                    'producto_id': item['productId'],
                    'cantidad': item['quantity']
                } for item in items
            ],
            'usuario_id': request.user.id,
            'fecha_reserva': timezone.now().isoformat()
        }
        
        print(f"📦 Enviando reserva a Stock API: {reserva_data}")
        
        # Llamar al endpoint real de reservas de Stock
        stock_url = f"{settings.STOCK_API_URL}/reservas"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(stock_url, json=reserva_data, headers=headers, timeout=10)
        
        print(f"📦 Respuesta Stock API: {response.status_code} - {response.text}")
        
        if response.status_code == 201:
            reserva_response = response.json()
            return {
                'success': True,
                'booking_id': reserva_response.get('id'),
                'message': 'Productos reservados exitosamente'
            }
        else:
            error_details = f"Error del servicio Stock: {response.status_code}"
            try:
                error_json = response.json()
                error_details = error_json.get('error', error_json.get('message', error_details))
            except:
                pass
                
            return {
                'success': False,
                'error': 'No se pudieron reservar los productos',
                'details': error_details
            }
            
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': 'No se pudo conectar al servicio Stock',
            'details': 'Error de conexión'
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'Timeout al conectar con servicio Stock',
            'details': 'El servicio no respondió a tiempo'
        }
    except Exception as e:
        print(f"❌ Error en reservar_productos_stock: {e}")
        return {
            'success': False,
            'error': f'Error inesperado: {str(e)}',
            'details': 'Error interno del servidor'
        }
        
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
    """Cancelar pedido Y RESERVA EN STOCK"""
    try:
        from .models import Order
        
        order = Order.objects.get(id=id, user=request.user)
        
        if order.status not in ['PENDING', 'PROCESSING']:
            return Response({
                'error': 'No se puede cancelar un pedido ya enviado',
                'code': 'CANNOT_CANCEL_SHIPPED_ORDER'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ CANCELAR RESERVA EN STOCK si existe
        if order.stock_booking_id:
            cancel_result = cancelar_reserva_stock(request, order.stock_booking_id)
            if not cancel_result.get('success'):
                print(f"⚠️ No se pudo cancelar reserva en Stock: {cancel_result.get('error')}")
        
        order.status = 'CANCELLED'
        order.save()
        
        return Response({
            'message': 'Pedido cancelado exitosamente',
            'reserva_cancelada': order.stock_booking_id is not None
        })
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Pedido no encontrado',
            'code': 'ORDER_NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)

# =============================================================================
# ENDPOINT EXTRA PARA CONSULTAR RESERVAS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_reservas_usuario(request):
    """GET /api/reservas - Obtener reservas del usuario en Stock"""
    try:
        social_auth = request.user.social_auth.get(provider='keycloak')
        access_token = social_auth.extra_data['access_token']
        
        reservas_url = f"{settings.STOCK_API_URL}/reservas"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Si la API de Stock permite filtrar por usuario
        params = {
            'usuarioId': request.user.id
        }
        
        response = requests.get(reservas_url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            reservas = response.json()
            return Response({
                'status': 'success',
                'total_reservas': len(reservas),
                'reservas': reservas
            })
        else:
            # Si no permite filtrar, obtener todas y filtrar localmente
            response_all = requests.get(reservas_url, headers=headers, timeout=10)
            if response_all.status_code == 200:
                todas_reservas = response_all.json()
                reservas_usuario = [
                    reserva for reserva in todas_reservas 
                    if reserva.get('usuarioId') == request.user.id
                ]
                return Response({
                    'status': 'success',
                    'total_reservas': len(reservas_usuario),
                    'reservas': reservas_usuario
                })
            else:
                return Response({
                    'error': 'Error obteniendo reservas',
                    'code': 'RESERVAS_ERROR'
                }, status=response_all.status_code)
            
    except Exception as e:
        print(f"❌ Error obteniendo reservas: {e}")
        return Response({
            'error': 'Error de conexión con servicio Stock',
            'code': 'CONNECTION_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#=============================================================================
# NUEVO ENDPOINT PARA OBTENER RESERVAS DESDE LA API EXTERNA DE LOGÍSTICA
#=============================================================================
from typing import Any, Dict, Optional
import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

API_BASE = getattr(settings, "LOGISTICA_API_BASE", "https://apilogistica.mmalgor.com.ar")
API_TIMEOUT = getattr(settings, "LOGISTICA_API_TIMEOUT", 10)  # segundos
SERVICE_TOKEN = getattr(settings, "LOGISTICA_API_TOKEN", None)  # opcional: token de servicio

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def obtener_reservas_usuario(request) -> Response:
    """
    Endpoint: GET /api/reservas
    - Recupera las reservas del usuario autenticado desde la API externa de logística.
    - Comportamiento:
      * Si la API externa acepta el mismo token del usuario, se reenvía Authorization.
      * Si preferís usar un token de servicio, configurá LOGISTICA_API_TOKEN en settings.
    Query params opcionales:
      - page, limit, desde, hasta, status, etc. (se reenvían tal cual a la API externa)
    """
    # Construir headers
    headers: Dict[str, str] = {"Accept": "application/json"}
    # Preferir token de servicio si está configurado
    if SERVICE_TOKEN:
        headers["Authorization"] = f"Bearer {SERVICE_TOKEN}"
    else:
        auth = request.META.get("HTTP_AUTHORIZATION")
        if auth:
            headers["Authorization"] = auth

    # Preparar query params: reenviamos todos los query params recibidos
    params = request.query_params.dict()

    # Si la API externa espera user_id, lo enviamos (por ejemplo)
    # asumimos que request.user tiene atributo id
    if "user_id" not in params:
        try:
            params["user_id"] = str(request.user.id)
        except Exception:
            # si no hay user id, no agregamos nada
            pass

    url = f"{API_BASE.rstrip('/')}/reservas"

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=API_TIMEOUT)
    except requests.RequestException as exc:
        return Response(
            {"detail": "Error de conexión con la API de logística", "error": str(exc)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
        try:
            data = resp.json()
        except ValueError:
            return Response(
                {"detail": "Respuesta inválida de la API de logística (no JSON)"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        # Opcional: aquí podrías validar/normalizar data con Pydantic antes de devolverla
        return Response(data, status=resp.status_code)
    else:
        return Response(
            {"detail": "Respuesta no JSON desde la API de logística", "raw": resp.text},
            status=resp.status_code,
        )

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def crear_reserva_stock(request, items, delivery_address):
    """Crear una reserva en el servicio Stock para los productos del carrito"""
    print(f"🔍 INICIANDO crear_reserva_stock")
    print(f"🔍 Items recibidos: {items}")
    print(f"🔍 User ID: {request.user.id}")
    
    try:
        # Obtener token del usuario
        social_auth = request.user.social_auth.get(provider='keycloak')
        access_token = social_auth.extra_data['access_token']
        print(f"🔍 Token: {access_token[:50]}...")
        
        # Generar ID único para la compra
        import random
        compra_id = f"COMPRA-PORTAL-{random.randint(100, 999):03d}"
        print(f"🔍 Compra ID: {compra_id}")
        
        # Preparar datos - USAR LOS NOMBRES CORRECTOS
        productos_data = []
        for item in items:
            # IMPORTANTE: Los items pueden tener 'productId' o 'producto_id'
            producto_id = item.get('productId') or item.get('producto_id')
            cantidad = item.get('quantity') or item.get('cantidad', 1)
            
            print(f"🔍 Procesando item: producto_id={producto_id}, cantidad={cantidad}")
            
            producto_data = {
                'productoId': producto_id,  # Usar el nombre que espera la API Stock
                'cantidad': cantidad,
                'precioUnitario': str(item.get('product', {}).get('price') or item.get('producto', {}).get('price', 0))
            }
            productos_data.append(producto_data)
            print(f"🔍 Producto preparado: {producto_data}")
        
        reserva_data = {
            'idCompra': compra_id,
            'usuarioId': request.user.id,
            'productos': productos_data
        }
        
        print(f"📦 ENVIANDO a Stock API: {reserva_data}")
        
        # Llamar al endpoint
        reservas_url = f"{settings.STOCK_API_URL}/reservas"
        print(f"🔍 URL: {reservas_url}")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print(f"🔍 Headers: {headers}")
        
        response = requests.post(reservas_url, json=reserva_data, headers=headers, timeout=10)
        
        print(f"📦 RESPUESTA Stock API:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Content: {response.text}")
        
        if response.status_code == 201:
            reserva_response = response.json()
            print(f"✅ RESERVA EXITOSA: {reserva_response}")
            return {
                'success': True,
                'reserva_id': reserva_response.get('idReserva'),
                'compra_id': reserva_response.get('idCompra'),
                'estado': reserva_response.get('estado'),
                'message': 'Reserva creada exitosamente',
                'data': reserva_response
            }
        else:
            print(f"❌ ERROR: {response.status_code} - {response.text}")
            return {
                'success': False,
                'error': f'Error del servicio Stock: {response.status_code}',
                'details': response.text
            }
            
    except Exception as e:
        print(f"💥 EXCEPCIÓN en crear_reserva_stock: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f'Error inesperado: {str(e)}'
        }
# DEBERIAMOS USAR UUID EN VEZ DE ID NUMERICO?
# def crear_reserva_stock(request, items, delivery_address):
#     """Crear una reserva en el servicio Stock para los productos del carrito"""
#     print(f"🔍 INICIANDO crear_reserva_stock")
#     print(f"🔍 Items: {items}")
    
#     try:
#         import random  # ✅ IMPORT DENTRO DE LA FUNCIÓN
        
#         # Obtener token y User ID de Keycloak
#         social_auth = request.user.social_auth.get(provider='keycloak')
#         access_token = social_auth.extra_data['access_token']
#         keycloak_user_id = social_auth.uid  # UUID de Keycloak
        
#         print(f"🔑 Keycloak User ID: {keycloak_user_id}")
#         print(f"🔑 Token: {access_token[:50]}...")
        
#         # Generar ID único para la compra
#         compra_id = f"COMPRA-PORTAL-{random.randint(100, 999):03d}"
#         print(f"🔍 Compra ID: {compra_id}")
        
#         # Preparar datos
#         productos_data = []
#         for item in items:
#             producto_data = {
#                 'productoId': item['productId'],
#                 'cantidad': item['quantity'],
#                 'precioUnitario': str(item['product']['price'])
#             }
#             productos_data.append(producto_data)
#             print(f"🔍 Producto: {producto_data}")
        
#         # ✅ USAR KEYCLOAK USER ID (UUID)
#         reserva_data = {
#             'idCompra': compra_id,
#             'usuarioId': keycloak_user_id,  # UUID de Keycloak
#             'productos': productos_data
#         }
        
#         print(f"📦 ENVIANDO a Stock API: {reserva_data}")
        
#         # Llamar al endpoint
#         reservas_url = f"{settings.STOCK_API_URL}/reservas"
#         print(f"🔍 URL: {reservas_url}")
        
#         headers = {
#             'Authorization': f'Bearer {access_token}',
#             'Content-Type': 'application/json'
#         }
        
#         response = requests.post(reservas_url, json=reserva_data, headers=headers, timeout=10)
        
#         print(f"📦 RESPUESTA Stock API:")
#         print(f"   Status: {response.status_code}")
#         print(f"   Content: {response.text}")
        
#         if response.status_code == 201:
#             reserva_response = response.json()
#             print(f"✅ RESERVA EXITOSA: {reserva_response}")
#             return {
#                 'success': True,
#                 'reserva_id': reserva_response.get('idReserva'),
#                 'compra_id': reserva_response.get('idCompra'),
#                 'estado': reserva_response.get('estado'),
#                 'message': 'Reserva creada exitosamente',
#                 'data': reserva_response
#             }
#         else:
#             print(f"❌ ERROR: {response.status_code} - {response.text}")
#             return {
#                 'success': False,
#                 'error': f'Error del servicio Stock: {response.status_code}',
#                 'details': response.text
#             }
            
#     except Exception as e:
#         print(f"💥 EXCEPCIÓN en crear_reserva_stock: {e}")
#         import traceback
#         traceback.print_exc()
#         return {
#             'success': False,
#             'error': f'Error inesperado: {str(e)}'
#         }

def cancelar_reserva_stock(request, reserva_id):
    """Cancelar una reserva en el servicio Stock"""
    try:
        social_auth = request.user.social_auth.get(provider='keycloak')
        access_token = social_auth.extra_data['access_token']
        
        # Llamar al endpoint para cancelar reserva
        cancel_url = f"{settings.STOCK_API_URL}/reservas/{reserva_id}/cancelar"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print(f"🔄 Cancelando reserva #{reserva_id} en Stock API...")
        
        response = requests.patch(cancel_url, headers=headers, timeout=10)
        
        print(f"📦 Respuesta cancelación: {response.status_code} - {response.text}")
        
        if response.status_code in [200, 204]:
            print(f"✅ Reserva {reserva_id} cancelada en Stock")
            return {
                'success': True,
                'message': 'Reserva cancelada exitosamente'
            }
        else:
            print(f"⚠️ No se pudo cancelar reserva {reserva_id}: {response.status_code}")
            return {
                'success': False,
                'error': f'No se pudo cancelar la reserva: {response.status_code} - {response.text}'
            }
            
    except Exception as e:
        print(f"❌ Error cancelando reserva: {e}")
        return {
            'success': False,
            'error': f'Error cancelando reserva: {str(e)}'
        }
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def obtener_envios_logistica(request) -> Response:
    """
    Endpoint: GET /api/envios
    Recupera los envíos del usuario desde la API de Logística
    """
    print(f"🚚 [LOGÍSTICA] Obteniendo envíos para usuario: {request.user.id}")
    
    try:
        # Obtener configuración desde settings
        LOGISTICA_API_URL = getattr(settings, "LOGI_API_URL", "https://apilogistica.mmalgor.com.ar/")
        LOGISTICA_CLIENT_ID = getattr(settings, "LOGI_API_CLIENT_ID", "grupo-12")
        LOGISTICA_CLIENT_SECRET = getattr(settings, "LOGI_API_CLIENT_SECRET", "")
        
        print(f"🔧 Config Logística - URL: {LOGISTICA_API_URL}")
        print(f"🔧 Config Logística - Client ID: {LOGISTICA_CLIENT_ID}")
        
        # Construir headers
        headers: Dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # OPCIÓN A: Usar token del usuario (si la API de Logística acepta tokens Keycloak)
        try:
            social_auth = request.user.social_auth.get(provider='keycloak')
            access_token = social_auth.extra_data['access_token']
            print(f"🔑 Usando token Keycloak del usuario: {access_token[:30]}...")
            headers["Authorization"] = f"Bearer {access_token}"
        except Exception as e:
            print(f"⚠️ No se pudo obtener token Keycloak: {e}")
            print(f"⚠️ Intentando con client credentials...")
            
            # OPCIÓN B: Usar client credentials específicos para Logística
            try:
                # Obtener token con client credentials para Logística
                token_data = obtener_token_logistica_client_credentials()
                if token_data:
                    headers["Authorization"] = f"Bearer {token_data}"
                else:
                    # OPCIÓN C: Reenviar token del request
                    auth = request.META.get("HTTP_AUTHORIZATION")
                    if auth:
                        headers["Authorization"] = auth
            except Exception as token_error:
                print(f"❌ Error con client credentials: {token_error}")
        
        # Preparar query params
        params = request.query_params.dict()
        
        # Si la API de Logística espera user_id, lo agregamos
        # Asumiendo que la API usa el ID de Django/Keycloak
        if "usuarioId" not in params and "userId" not in params:
            try:
                params["usuarioId"] = str(request.user.id)
            except Exception:
                pass
        
        url = f"{LOGISTICA_API_URL.rstrip('/')}/shipping"
        print(f"🔍 Llamando a API Logística: {url}")
        print(f"🔍 Params: {params}")
        print(f"🔍 Headers: {{'Authorization': 'Bearer ...'}}")
        
        # Hacer la petición
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"📦 Respuesta API Logística: {resp.status_code}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                print(f"✅ Envíos obtenidos: {len(data) if isinstance(data, list) else 'dict'}")
                return Response(data, status=resp.status_code)
            except ValueError:
                return Response(
                    {"detail": "Respuesta inválida de la API de logística (no JSON)", "raw": resp.text[:200]},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
        else:
            error_msg = f"Error API Logística: {resp.status_code}"
            try:
                error_data = resp.json()
                error_msg = error_data.get("error", error_data.get("message", error_msg))
                print(f"❌ {error_msg}")
            except:
                print(f"❌ {error_msg} - {resp.text[:200]}")
            
            return Response(
                {"detail": error_msg},
                status=resp.status_code if 400 <= resp.status_code < 600 else status.HTTP_502_BAD_GATEWAY,
            )
            
    except requests.RequestException as exc:
        print(f"❌ Error de conexión con API Logística: {exc}")
        return Response(
            {"detail": "Error de conexión con la API de logística", "error": str(exc)},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {"detail": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

def obtener_token_logistica_client_credentials():
    """
    Obtener token de acceso para la API de Logística usando client credentials
    """
    try:
        LOGI_API_URL = getattr(settings, "LOGI_API_URL", "https://apilogistica.mmalgor.com.ar/")
        CLIENT_ID = getattr(settings, "LOGI_API_CLIENT_ID", "grupo-12")
        CLIENT_SECRET = getattr(settings, "LOGI_API_CLIENT_SECRET", "")
        
        print(f"🔐 Intentando obtener token para {CLIENT_ID} en {LOGI_API_URL}")
        
        # URL de Keycloak para obtener token
        token_url = "https://keycloak.mmalgor.com.ar/realms/ds-2025-realm/protocol/openid-connect/token"
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        print(f"🔐 Enviando solicitud a Keycloak...")
        response = requests.post(token_url, data=data, headers=headers, timeout=10)
        
        print(f"🔐 Respuesta Keycloak: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            print(f"✅ Token obtenido exitosamente")
            return access_token
        else:
            print(f"❌ Error obteniendo token client_credentials: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en obtener_token_logistica_client_credentials: {e}")
        import traceback
        traceback.print_exc()
        return None
           
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_envios_usuario(request):
    """
    GET /api/envios - Obtener envíos del usuario desde la API de Logística
    """
    try:
        # Configuración
        LOGISTICA_API_URL = getattr(settings, 'LOGI_API_URL', 'https://apilogistica.mmalgor.com.ar')
        
        # Obtener token del usuario
        social_auth = request.user.social_auth.get(provider='keycloak')
        access_token = social_auth.extra_data['access_token']
        
        # Preparar headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Intentar obtener los envíos del usuario
        # La API de logística podría tener diferentes endpoints:
        # Opción 1: /envios?usuario_id=xxx
        # Opción 2: /envios/usuario/xxx
        # Consultamos cuál es el formato correcto
        
        # Primero intentamos obtener todos los envíos
        url = f"{LOGISTICA_API_URL}/shipping"
        print(f"🔍 Consultando API Logística: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            envios = response.json()
            
            # Filtrar por usuario si la API no lo hace automáticamente
            envios_usuario = []
            for envio in envios:
                # Verificar si el envío pertenece al usuario
                # Dependiendo de cómo la API devuelve los datos
                usuario_id = envio.get('usuario_id') or envio.get('userId') or envio.get('cliente_id')
                if usuario_id and str(usuario_id) == str(request.user.id):
                    envios_usuario.append(envio)
                # Si no hay filtro de usuario, mostrar todos (para testing)
                elif not usuario_id:
                    envios_usuario.append(envio)
            
            return Response({
                'status': 'success',
                'total_envios': len(envios_usuario),
                'envios': envios_usuario
            })
        else:
            print(f"❌ Error API Logística: {response.status_code} - {response.text}")
            return Response({
                'error': f'Error obteniendo envíos: {response.status_code}',
                'details': response.text
            }, status=response.status_code)
            
    except Exception as e:
        print(f"❌ Error en obtener_envios_usuario: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': 'Error de conexión con el servicio Logística',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# En api_views.py - Agrega esta función
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_envio_logistica(request):
    """
    POST /api/envios/crear - Crear un nuevo envío en Logística
    Se llama automáticamente después del checkout
    """
    print(f"🚚 [LOGÍSTICA] Creando envío para usuario: {request.user.id}")
    
    try:
        from datetime import datetime
        
        # Obtener datos del request
        data = request.data
        
        # Validar datos mínimos
        required_fields = ['orden_id', 'direccion_entrega', 'ciudad', 'provincia']
        for field in required_fields:
            if field not in data:
                return Response({
                    'error': f'Campo requerido faltante: {field}',
                    'code': 'MISSING_FIELD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener configuración
        LOGISTICA_API_URL = getattr(settings, "LOGI_API_URL", "https://apilogistica.mmalgor.com.ar/")
        LOGISTICA_CLIENT_ID = getattr(settings, "LOGI_API_CLIENT_ID", "grupo-12")
        LOGISTICA_CLIENT_SECRET = getattr(settings, "LOGI_API_CLIENT_SECRET", "")
        
        # Preparar headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Obtener token (similar a la función de consulta)
        try:
            social_auth = request.user.social_auth.get(provider='keycloak')
            access_token = social_auth.extra_data['access_token']
            headers["Authorization"] = f"Bearer {access_token}"
        except Exception as e:
            print(f"⚠️ Usando client credentials para crear envío")
            token = obtener_token_logistica_client_credentials()
            if token:
                headers["Authorization"] = f"Bearer {token}"
            else:
                # Reenviar token del request como última opción
                auth = request.META.get("HTTP_AUTHORIZATION")
                if auth:
                    headers["Authorization"] = auth
        
        # Preparar datos para la API de Logística
        envio_data = {
            "orden_id": data['orden_id'],
            "usuario_id": str(request.user.id),
            "cliente_nombre": f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            "cliente_email": request.user.email,
            "direccion_entrega": data['direccion_entrega'],
            "ciudad": data['ciudad'],
            "provincia": data['provincia'],
            "codigo_postal": data.get('codigo_postal', ''),
            "telefono": data.get('telefono', ''),
            "instrucciones": data.get('instrucciones', ''),
            "estado": "PENDIENTE",
            "fecha_creacion": datetime.now().isoformat(),
            "peso_total": data.get('peso_total', 0),
            "dimensiones": data.get('dimensiones', {}),
            # Información de productos si está disponible
            "productos": data.get('productos', [])
        }
        
        # URL para crear envío
        url = f"{LOGISTICA_API_URL.rstrip('/')}/envios"
        print(f"🔍 Creando envío en: {url}")
        print(f"📦 Datos del envío: {envio_data}")
        
        # Llamar a la API de Logística
        response = requests.post(url, json=envio_data, headers=headers, timeout=10)
        
        print(f"📦 Respuesta creación envío: {response.status_code}")
        
        if response.status_code in [200, 201]:
            envio_response = response.json()
            print(f"✅ Envío creado exitosamente: {envio_response.get('id', 'N/A')}")
            
            # Actualizar la orden con el tracking ID si está disponible
            try:
                from .models import Order
                order = Order.objects.get(id=data['orden_id'], user=request.user)
                order.logistics_tracking_id = envio_response.get('id') or envio_response.get('tracking_id')
                order.save()
                print(f"✅ Orden actualizada con tracking: {order.logistics_tracking_id}")
            except Exception as e:
                print(f"⚠️ No se pudo actualizar orden: {e}")
            
            return Response({
                'success': True,
                'message': 'Envío creado exitosamente',
                'envio_id': envio_response.get('id'),
                'tracking_id': envio_response.get('tracking_id'),
                'estado': envio_response.get('estado', 'PENDIENTE'),
                'data': envio_response
            }, status=status.HTTP_201_CREATED)
        else:
            error_msg = f"Error creando envío: {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get("error", error_data.get("message", error_msg))
            except:
                error_msg += f" - {response.text[:200]}"
            
            print(f"❌ {error_msg}")
            
            return Response({
                'success': False,
                'error': error_msg,
                'code': 'LOGISTICS_API_ERROR'
            }, status=response.status_code)
            
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return Response({
            'success': False,
            'error': f'Error de conexión con el servicio de logística: {str(e)}',
            'code': 'CONNECTION_ERROR'
        }, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}',
            'code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def consultar_estado_envio_logistica(shipping_id):
    """
    Consultar el estado actual de un envío usando shipping_id
    """
    try:
        LOGI_API_URL = getattr(settings, 'LOGI_API_URL', 'https://apilogistica.mmalgor.com.ar/')
        
        # Obtener token
        token = obtener_token_logistica_client_credentials()
        if not token:
            return None
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        # ✅ USAR SHIPPING_ID DIRECTAMENTE
        url = f"{LOGI_API_URL.rstrip('/')}/shipping/{shipping_id}"
        print(f"🔍 Consultando estado de envío: {url}")
        
        response = requests.get(url, headers=headers, timeout=3)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error consultando envío {shipping_id}: {e}")
        return None