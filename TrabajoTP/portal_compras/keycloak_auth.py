from django.http import JsonResponse
from keycloak import KeycloakOpenID
from django.conf import settings
from functools import wraps

# Configuración de Keycloak para grupo-07
keycloak_openid = KeycloakOpenID(
    server_url=settings.KEYCLOAK_SERVER_URL,
    client_id=settings.KEYCLOAK_CLIENT_ID,  # grupo-07
    realm_name=settings.KEYCLOAK_REALM,     # ds-2025-realm
    client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
)

def keycloak_login_required(view_func):
    """
    DECORATOR que protege una view con Keycloak
    
    Cómo funciona:
    1. Otro equipo obtiene token de Keycloak
    2. Llaman a tu API con: Authorization: Bearer <token>
    3. Este decorator verifica el token con Keycloak
    4. Si es válido, permite el acceso
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Obtener el token del header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                "error": "Token requerido", 
                "message": "Usa: Authorization: Bearer <token>"
            }, status=401)
        
        token = auth_header.split(' ')[1]
        
        try:
            # ✅ VERIFICAR TOKEN CON KEYCLOAK
            userinfo = keycloak_openid.userinfo(token)
            
            # Guardar info del usuario en el request
            request.keycloak_user = userinfo
            request.keycloak_token = token
            
            # Ejecutar la view original
            return view_func(request, *args, **kwargs)
            
        except Exception as e:
            return JsonResponse({
                "error": "Token inválido", 
                "message": str(e)
            }, status=401)
    
    return wrapper

def obtener_token_client_credentials():
    """Obtener token usando client credentials para usuarios no autenticados"""
    try:
        from keycloak import KeycloakOpenID
        from django.conf import settings
        
        keycloak_openid = KeycloakOpenID(
            server_url=settings.KEYCLOAK_SERVER_URL,
            client_id=settings.KEYCLOAK_CLIENT_ID,
            realm_name=settings.KEYCLOAK_REALM,
            client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
        )
        
        token = keycloak_openid.token(grant_type="client_credentials")
        return token.get('access_token')
        
    except Exception as e:
        print(f"❌ Error obteniendo token client_credentials: {e}")
        return None