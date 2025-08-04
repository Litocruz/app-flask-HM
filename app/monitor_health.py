# monitor_health.py

import requests
import sys
import time

def check_app_health(url):
    """
    Verifica la salud de la aplicación haciendo una petición GET a su endpoint.
    """
    try:
        response = requests.get(url, timeout=5)
        # Verifica si el código de estado es 200 (OK)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print(f"[{time.ctime()}] OK: La aplicación está saludable y respondiendo.")
                return True
        print(f"[{time.ctime()}] ERROR: La aplicación devolvió el código de estado {response.status_code} o un estado de salud incorrecto.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[{time.ctime()}] ERROR: No se pudo conectar con la aplicación en {url}. Error: {e}")
        return False

if __name__ == "__main__":
    # URL del health check. Se asume que la app está corriendo en el puerto 5000.
    app_url = "http://localhost:5000/health"
    
    # Intenta verificar la salud. Si falla, el script termina con un código de error 1.
    if not check_app_health(app_url):
        sys.exit(1)