from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import requests
from django.conf import settings

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
        'user': request.session.get('user')
    })

def login_view(request):
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
                
                # Guardar en sesión con datos REALES del usuario
                request.session['access_token'] = result['accessToken']
                request.session['user'] = result['user'] 
                
                return JsonResponse({
                    'success': True,
                    'token': result['accessToken'],
                    'user': result['user']
                })
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
    
    return render(request, 'portal_compras/login.html')
    
def registro_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Llamar a nuestra API de registro
            response = requests.post(
                'http://127.0.0.1:8000/api/auth/register',
                json=data
            )
            
            if response.status_code == 201:
                result = response.json()
                
                # Guardar en sesión si viene token
                if 'accessToken' in result:
                    request.session['access_token'] = result['accessToken']
                    request.session['user'] = result['user']
                
                return JsonResponse({
                    'success': True,
                    'message': result.get('message', 'Registro exitoso'),
                    'user': result.get('user')
                })
            else:
                result = response.json()
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Error en el registro')
                }, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Error en el servidor'
            }, status=500)
    
    return render(request, 'portal_compras/registro.html')

def lista_productos(request):
    """Vista para lista de productos"""
    productos = []  # Por ahora vacío, luego cargaremos desde API
    return render(request, 'portal_compras/index.html', {
        'productos': productos,
        'user': request.session.get('user')
    })

def logout_view(request):
    """Cerrar sesión"""
    request.session.flush()
    return redirect('index')

def shopcart_view(request):
    """Página del carrito - frontend"""
    carrito_data = {'items': [], 'total': 0}
    
    # Verificar si hay usuario en sesión
    user_session = request.session.get('user')
    token = request.session.get('access_token')
    
    if user_session and token:
        try:
            # Llamar a nuestra API para obtener el carrito con el token OAuth2
            response = requests.get(
                'http://127.0.0.1:8000/api/shopcart',
                headers={'Authorization': f"Bearer {token}"}
            )
            print(f"🔍 API Carrito - Status: {response.status_code}")  # Debug
            
            if response.status_code == 200:
                carrito_data = response.json()
                print(f"✅ Carrito obtenido: {len(carrito_data.get('items', []))} items")  # Debug
            else:
                print(f"❌ Error API Carrito: {response.status_code} - {response.text}")  # Debug
        except Exception as e:
            print(f"❌ Excepción en shopcart_view: {e}")  # Debug
    
    # Calcular subtotales para cada item
    for item in carrito_data['items']:
        item['subtotal'] = item.get('quantity', 0) * item.get('product', {}).get('price', 0)
    
    return render(request, 'portal_compras/carrito.html', {
        'carrito': carrito_data,
        'user': user_session 
    })

def orders_view(request):
    """Vista para el historial de órdenes"""
    orders_data = []
    
    if request.user.is_authenticated and request.session.get('access_token'):
        try:
            token = request.session['access_token']
            response = requests.get(
                'http://127.0.0.1:8000/api/shopcart/history',
                headers={'Authorization': f"Bearer {token}"}
            )
            if response.status_code == 200:
                orders_data = response.json()
        except Exception as e:
            print(f"Error cargando órdenes: {e}")
    
    return render(request, 'portal_compras/ordenes.html', {
        'orders': orders_data,
        'user': request.session.get('user')
    })

def orders_view(request):
    """Vista para el historial de órdenes"""
    orders_data = []
    
    user_session = request.session.get('user')
    token = request.session.get('access_token')
    
    if user_session and token:
        try:
            response = requests.get(
                'http://127.0.0.1:8000/api/shopcart/history',
                headers={'Authorization': f"Bearer {token}"}
            )
            print(f"🔍 API Historial - Status: {response.status_code}")
            
            if response.status_code == 200:
                orders_data = response.json()
                print(f"✅ Órdenes obtenidas: {len(orders_data)}")
                
                # Calcular subtotales para cada item
                for order in orders_data:
                    for item in order['items']:
                        item['subtotal'] = item['quantity'] * item['product']['price']
                        
            else:
                print(f"❌ Error API Historial: {response.status_code}")
        except Exception as e:
            print(f"❌ Error cargando historial: {e}")
    
    return render(request, 'portal_compras/ordenes.html', {
        'orders': orders_data,
        'user': user_session
    })

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
        'user': request.session.get('user'),
        'query': query,
        'categoria_seleccionada': categoria,
        'categorias': categorias
    })