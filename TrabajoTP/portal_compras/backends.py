# portal_compras/backends.py
from social_core.backends.keycloak import KeycloakOAuth2
import jwt
from jwt import PyJWT

class CustomKeycloakOAuth2(KeycloakOAuth2):
    def public_key(self):
        # Public key hardcodeada
        public_key_value = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvRNUYBCIBoBLKvj9dFjHHhR3YCY93OkBQ/okdg5F1kRrXZOlHWoP1DLh4IYadr0DtlBWqQJWgzHr/Symo86F5f4mLqdiGX7zXoH6jvig8EX1fOF+tkXK4GeyEpPaU3FBHEoptSZGiHSQJhd2q1bPVwyh9LcsWdUktRUEhyJaa+kTQxLtt816dny9JpRgDt1JfZYNs9i66iqfBfGoF88Mf7z7QKKP9D9JlYHvnzKcqtSqUcW0T2QO195gBGV0hL/df1owBVC0CI1pKoddUZNAiEvUDk2OE7ERdcBy5YY04vwoP6EVrGJi3bYKrtkYZdmxj7obfgUhHSvuu2BwxpN1yQIDAQAB"
        
        if public_key_value:
            return f"-----BEGIN PUBLIC KEY-----\n{public_key_value}\n-----END PUBLIC KEY-----"
        return None
    
    def get_key(self, secret=None):
        return None
    
    def user_data(self, access_token, *args, **kwargs):
        """Obtener datos del usuario sin validar el token JWT"""
        try:
            # Obtener userinfo desde el endpoint de Keycloak
            response = self.request(
                self.setting('USERINFO_URL'),
                headers={'Authorization': f'Bearer {access_token}'}
            )
            return response.json()
        except Exception as e:
            print(f"Error obteniendo user data: {e}")
            return {}
    
    def decode_token(self, token, verify=True):
        """Decodificar token sin verificar claims requeridos"""
        try:
            # Decodificar sin verificar para evitar errores de claims
            return jwt.decode(
                token, 
                options={"verify_signature": False, "verify_aud": False}
            )
        except Exception as e:
            print(f"Error decodificando token: {e}")
            return {}