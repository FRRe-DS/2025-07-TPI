from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import requests
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User

def index(request):
    """Página principal con productos de prueba"""
    productos = [
        {
            'id': 1,
            'name': 'Notebook Gamer',
            'description': 'Laptop para gaming de alto rendimiento',
            'price': 1500.00,
            'stock': 10,
            'category': 'Tecnología'
        },
        {
            'id': 2,
            'name': 'Mouse Inalámbrico',
            'description': 'Mouse ergonómico con sensor óptico',
            'price': 45.99,
            'stock': 25,
            'category': 'Accesorios'
        },
        {
            'id': 3, 
            'name': 'Teclado Mecánico',
            'description': 'Teclado gaming con switches mecánicos',
            'price': 89.99,
            'stock': 15,
            'category': 'Accesorios'
        },
        {
            'id': 4,
            'name': 'Monitor 24"',
            'description': 'Monitor Full HD para trabajo y gaming',
            'price': 299.99,
            'stock': 8,
            'category': 'Tecnología'
        },
        {
            'id': 5,
            'name': 'Auriculares Bluetooth',
            'description': 'Auriculares inalámbricos con cancelación de ruido',
            'price': 129.99,
            'stock': 20,
            'category': 'Audio'
        }
    ]
    
    return render(request, 'portal_compras/index.html', {
        'productos': productos,
        'user': request.user if request.user.is_authenticated else None
    })

def login_view(request):
    """Vista de login que muestra opciones de autenticación"""
    if request.user.is_authenticated:
        return redirect('index')
    
    return render(request, 'portal_compras/login.html', {
        'keycloak_enabled': True,
        'keycloak_url': f'{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/auth'
    })

def registro_view(request):
    """Redirige a Keycloak para registro - EL REGISTRO SE HACE EN KEYCLOAK"""
    # Redirigir directamente a Keycloak para registro
    keycloak_registro_url = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/"
        f"protocol/openid-connect/registrations"
        f"?client_id={settings.KEYCLOAK_CLIENT_ID}&response_type=code&scope=openid profile email&redirect_uri=http://localhost:8000/social-auth/complete/keycloak/"
    )
    return redirect(keycloak_registro_url)

def lista_productos(request):
    """Vista para lista de productos con búsqueda"""
    productos = []
    query = request.GET.get('q', '')  # Término de búsqueda
    categoria = request.GET.get('categoria', '')  # Filtro por categoría
    
    try:
        # Podríamos conectar con el servicio Stock aquí
        # Por ahora usamos el mismo mock del carrito
        productos_mock = [
            {
                'id': 1,
                'name': 'Notebook Gamer', 
                'description': 'Laptop para gaming de alto rendimiento',
                'price': 1500.00,
                'stock': 10,
                'category': 'Tecnología'
            },
            {
                'id': 2,
                'name': 'Mouse Inalámbrico',
                'description': 'Mouse ergonómico con sensor óptico',
                'price': 45.99,
                'stock': 25,
                'category': 'Accesorios'
            },
            {
                'id': 3, 
                'name': 'Teclado Mecánico',
                'description': 'Teclado gaming con switches mecánicos',
                'price': 89.99,
                'stock': 15,
                'category': 'Accesorios'
            },
            {
                'id': 4,
                'name': 'Monitor 24"',
                'description': 'Monitor Full HD para trabajo y gaming',
                'price': 299.99,
                'stock': 8,
                'category': 'Tecnología'
            },
            {
                'id': 5,
                'name': 'Auriculares Bluetooth',
                'description': 'Auriculares inalámbricos con cancelación de ruido',
                'price': 129.99,
                'stock': 20,
                'category': 'Audio'
            },
            {
                'id': 6,
                'name': 'Tablet 10"',
                'description': 'Tablet Android con pantalla Full HD',
                'price': 199.99,
                'stock': 12,
                'category': 'Tecnología'
            },
            {
                'id': 7,
                'name': 'Smartwatch',
                'description': 'Reloj inteligente con monitor de actividad',
                'price': 79.99,
                'stock': 30,
                'category': 'Wearables'
            },
            {
                'id': 8,
                'name': 'Cargador Rápido',
                'description': 'Cargador USB-C de 65W',
                'price': 29.99,
                'stock': 50,
                'category': 'Accesorios'
            }
        ]
        
        # Aplicar filtros
        productos_filtrados = productos_mock
        
        if query:
            productos_filtrados = [p for p in productos_filtrados 
                                 if query.lower() in p['name'].lower() 
                                 or query.lower() in p['description'].lower()]
        
        if categoria:
            productos_filtrados = [p for p in productos_filtrados 
                                 if p['category'].lower() == categoria.lower()]
        
        productos = productos_filtrados
        
    except Exception as e:
        print(f"Error cargando productos: {e}")
    
    # Obtener categorías únicas para el filtro
    categorias = sorted(list(set([p['category'] for p in productos]))) if productos else []
    
    return render(request, 'portal_compras/productos.html', {
        'productos': productos,
        'user': request.user if request.user.is_authenticated else None,
        'query': query,
        'categoria_seleccionada': categoria,
        'categorias': categorias
    })

def logout_view(request):
    """Cerrar sesión tanto en Django como en Keycloak"""
    # Limpiar sesión de Django
    auth_logout(request)
    
    # Redirigir a logout de Keycloak si está autenticado via Keycloak
    if hasattr(request, 'user') and request.user.is_authenticated:
        # Verificar si es autenticación social
        social_auth = getattr(request.user, 'social_auth', None)
        if social_auth and social_auth.filter(provider='keycloak').exists():
            keycloak_logout_url = (
                f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/"
                f"protocol/openid-connect/logout"
            )
            return redirect(keycloak_logout_url)
    
    return redirect('index')

def shopcart_view(request):
    """Página del carrito - frontend"""
    carrito_data = {'items': [], 'total': 0}
    
    if request.user.is_authenticated:
        try:
            # ✅ ACCESO DIRECTO a la base de datos - sin depender de la API
            from .models import ShoppingCart
            carrito, created = ShoppingCart.objects.get_or_create(user=request.user)
            
            print(f"✅ Carrito obtenido directamente: {len(carrito.items)} items")
            
            carrito_data = {
                'items': carrito.items,
                'total': carrito.calculate_total()  # Esto calcula el total
            }
            
        except Exception as e:
            print(f"❌ Error en shopcart_view: {e}")
    
    # Calcular subtotales para cada item
    for item in carrito_data['items']:
        item['subtotal'] = item.get('quantity', 0) * item.get('product', {}).get('price', 0)
    
    return render(request, 'portal_compras/carrito.html', {
        'carrito': carrito_data,
        'user': request.user if request.user.is_authenticated else None
    })
    
def orders_view(request):
    """Vista para el historial de órdenes - ACCESO DIRECTO A BD"""
    orders_data = []
    
    print("🎯 ORDERS_VIEW EJECUTÁNDOSE")
    print(f"🎯 Usuario: {request.user} (Autenticado: {request.user.is_authenticated})")
    
    if request.user.is_authenticated:
        try:
            # ✅ ACCESO DIRECTO a la base de datos - sin depender de la API
            from .models import Order, OrderItem
            orders = Order.objects.filter(user=request.user).prefetch_related('items')
            
            print(f"✅ Órdenes obtenidas directamente: {orders.count()}")
            
            for order in orders:
                order_data = {
                    'id': order.id,
                    'date': order.date.isoformat(),
                    'status': order.status,
                    'total': float(order.total),
                    'delivery_address': order.delivery_address,
                    'payment_method': order.payment_method,
                    'items': []
                }
                
                for item in order.items.all():
                    order_data['items'].append({
                        'productId': item.productId,
                        'quantity': item.quantity,
                        'product': {
                            'id': item.productId,
                            'name': f'Producto {item.productId}',  # Podemos mejorar esto después
                            'price': float(item.price)
                        }
                    })
                
                orders_data.append(order_data)
                print(f"✅ Orden {order.id}: {len(order_data['items'])} items")
                
        except Exception as e:
            print(f"❌ Error en orders_view: {e}")
            import traceback
            traceback.print_exc()
    
    return render(request, 'portal_compras/ordenes.html', {
        'orders': orders_data,
        'user': request.user if request.user.is_authenticated else None
    })
    
# Vista para manejar login tradicional via AJAX
def login_ajax_view(request):
    """Maneja el login tradicional via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Llamar a nuestra API de login
            response = requests.post(
                'http://127.0.0.1:8000/api/auth/login',
                json={
                    'email': data.get('email'),
                    'password': data.get('password')
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Autenticar al usuario en Django
                from django.contrib.auth import authenticate, login
                user = authenticate(
                    request, 
                    username=data.get('email'), 
                    password=data.get('password')
                )
                
                if user:
                    login(request, user)
                    
                    return JsonResponse({
                        'success': True,
                        'token': result['accessToken'],
                        'user': result['user']
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Error al autenticar en el sistema'
                    }, status=401)
            else:
                result = response.json()
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Credenciales inválidas')
                }, status=401)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Error en el servidor'
            }, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista para perfil de usuario
@login_required
def profile_view(request):
    """Vista del perfil de usuario"""
    user = request.user
    profile_data = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'date_joined': user.date_joined,
    }
    
    # Verificar si es autenticación social (Keycloak)
    is_keycloak_user = False
    if hasattr(user, 'social_auth'):
        social_auth = user.social_auth.filter(provider='keycloak')
        if social_auth.exists():
            is_keycloak_user = True
    
    return render(request, 'portal_compras/profile.html', {
        'profile': profile_data,
        'is_keycloak_user': is_keycloak_user,
        'user': user
    })

# Vista para manejar errores de login
def login_error_view(request):
    """Vista para mostrar errores de autenticación"""
    return render(request, 'portal_compras/login_error.html', {
        'user': request.user if request.user.is_authenticated else None
    })