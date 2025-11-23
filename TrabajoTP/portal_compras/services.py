# portal_compras/services.py
import requests
from django.conf import settings
import json

class StockService:
    @staticmethod
    def obtener_productos():
        """Obtiene todos los productos del servicio Stock"""
        try:
            print(f"🔍 Conectando a: {settings.STOCK_API_URL}/api/stock/product")
            response = requests.get(
                f"{settings.STOCK_API_URL}/api/stock/product",
                timeout=5
            )
            print(f"📡 Respuesta HTTP: {response.status_code}")
            
            if response.status_code == 200:
                productos = response.json()
                print(f"✅ Productos obtenidos: {len(productos)}")
                return productos
            else:
                print(f"❌ Error en API Stock: {response.status_code}")
                return []
                
        except requests.exceptions.ConnectionError:
            print("❌ No se pudo conectar al servicio Stock")
            return []
        except requests.exceptions.Timeout:
            print("❌ Timeout conectando al servicio Stock")
            return []
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return []

    @staticmethod
    def obtener_producto(producto_id):
        """Obtiene un producto específico"""
        try:
            response = requests.get(
                f"{settings.STOCK_API_URL}/api/stock/product/{producto_id}",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

class LogisticaService:
    @staticmethod
    def crear_tracking(datos_tracking):
        """Crea un tracking en el servicio Logística"""
        try:
            response = requests.post(
                f"{settings.LOGISTICA_API_URL}/api/logistics/tracking",
                json=datos_tracking,
                timeout=5
            )
            if response.status_code == 201:
                return response.json()
            return None
        except:
            return None