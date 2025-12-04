from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import requests
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.shortcuts import get_object_or_404

# Configuración Keycloak
KEYCLOAK_SERVER_URL = settings.KEYCLOAK_SERVER_URL
KEYCLOAK_REALM = settings.KEYCLOAK_REALM
KEYCLOAK_CLIENT_ID = settings.KEYCLOAK_CLIENT_ID

# =============================================================================
# VISTAS PRINCIPALES (PÁGINAS HTML)
# =============================================================================

def index(request):
    """Página principal con productos destacados"""
    productos_destacados = []
    
    try:
        # Obtener token para la API (client credentials para no autenticados)
        access_token = None
        
        if request.user.is_authenticated:
            # Intentar con token de usuario autenticado
            try:
                social_auth = request.user.social_auth.get(provider='keycloak')
                access_token = social_auth.extra_data['access_token']
                print(f"🔄 Home: Usando token de usuario {request.user.username}")
            except Exception as e:
                print(f"❌ Home: Error con token de usuario: {e}")
                access_token = None
        
        # Si no hay token de usuario, usar client credentials
        if access_token:
            logistica_url = "https://apilogistica.mmalgor.com.ar"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(logistica_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                ShippingDetails_api = response.json()
                print(f"✅ Home: {len(ShippingDetails_api)} detalles de compra obtenidos")
                
          
                envio_formateado = {
                    'Orderid': ShippingDetails_api.get('order_id'),
                    'Delivery_address': ShippingDetails_api.get('delivery_address'),
                    'Products': ShippingDetails_api.get('products'),
                    'Status': ShippingDetails_api.get('status'),
                    'Transport_type': ShippingDetails_api.get('transport_type'),
                    'Carrier_name': ShippingDetails_api.get('carrier_name'),
                    'Estimated_delivery_at': ShippingDetails_api.get('estimated_delivery_at'),
                    'Total_cost': ShippingDetails_api.get('total_cost'),
                }
                    
                    
                print(f"🏠 Home: Mostrando {len(productos_destacados)} productos destacados")
                
            else:
                print(f"❌ Home: Error Logistica API: {response.status_code}")
        else:
            print("❌ Home: No se pudo obtener token")

    except Exception as e:
        print(f"💥 Home: Error general: {e}")
        import traceback
        traceback.print_exc()
    
    return render(request, 'portal_compras/index.html', {
        'user': request.user if request.user.is_authenticated else None,
        'productos_destacados': envio_formateado
    })