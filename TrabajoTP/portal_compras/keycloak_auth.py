from django.http import JsonResponse
from keycloak import KeycloakOpenID
from django.conf import settings
from functools import wraps

# En keycloak_auth.py - CORREGIR el error de server_url
from keycloak import KeycloakOpenID
from django.conf import settings

# Configuración de Keycloak para grupo-07
keycloak_openid = KeycloakOpenID(
    server_url=settings.KEYCLOAK_SERVER_URL,
    client_id=settings.KEYCLOAK_CLIENT_ID,
    realm_name=settings.KEYCLOAK_REALM,
    client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
)

def keycloak_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        print(f"🔐 [DEBUG] keycloak_login_required - INICIANDO VERIFICACIÓN")
        
        # Obtener el token del header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            print(f"❌ No hay token Bearer")
            return JsonResponse({
                "error": "Token requerido", 
                "message": "Usa: Authorization: Bearer <token>"
            }, status=401)
        
        token = auth_header.split(' ')[1]
        
        try:
            # ✅ VERIFICAR TOKEN CON KEYCLOAK - CORREGIDO
            print(f"🔐 Verificando token con Keycloak...")
            
            # IMPORTANTE: La configuración está arriba, no acceder a server_url directamente
            print(f"🔐 Config Keycloak - Server: {settings.KEYCLOAK_SERVER_URL}")
            print(f"🔐 Config Keycloak - Realm: {settings.KEYCLOAK_REALM}")
            print(f"🔐 Config Keycloak - Client ID: {settings.KEYCLOAK_CLIENT_ID}")
            
            # Verificar token
            userinfo = keycloak_openid.userinfo(token)
            print(f"✅ Token válido - Usuario: {userinfo.get('preferred_username')}")
            
            # Guardar info del usuario en el request
            request.keycloak_user = userinfo
            request.keycloak_token = token
            
            # Ejecutar la view original
            return view_func(request, *args, **kwargs)
            
        except Exception as e:
            print(f"❌ Error verificando token: {e}")
            
            # Verificar si es error de token expirado
            import jwt
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
                exp = decoded.get('exp')
                from datetime import datetime
                if exp and datetime.fromtimestamp(exp) < datetime.now():
                    print(f"❌ TOKEN EXPIRADO!")
                    return JsonResponse({
                        "error": "Token expirado",
                        "message": "El token ha expirado, obtén uno nuevo",
                        "code": "TOKEN_EXPIRED"
                    }, status=401)
            except:
                pass
                
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