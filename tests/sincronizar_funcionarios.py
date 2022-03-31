"""
Sinconizar funcionarios con la API de RRHH Personal
"""
import os
import requests
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry
from tabulate import tabulate

load_dotenv()  # Take environment variables from .env

LLAMADOS_CANTIDAD = 4
CUATRO_SEGUNDOS = 4


class ConfigurationError(Exception):
    """Error de configuración"""


class StatusCodeNot200Error(Exception):
    """Error de status code"""


class ResponseJSONError(Exception):
    """Error de respuesta JSON"""


def get_token(base_url, username, password):
    """Iniciar sesion y obtener token"""
    if base_url is None or username is None or password is None:
        raise ConfigurationError("Falta configurar las variables de entorno")
    response = requests.post(
        url=f"{base_url}/token",
        data={"username": username, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    respuesta = response.json()
    if "access_token" not in respuesta:
        raise ResponseJSONError("Error en la respuesta, falta el token")
    return respuesta["access_token"]


@sleep_and_retry
@limits(calls=LLAMADOS_CANTIDAD, period=CUATRO_SEGUNDOS)
def get_personas(base_url, token, limit, offset):
    """Consultar personas"""
    response = requests.get(
        url=f"{base_url}/v1/personas",
        headers={"authorization": f"Bearer {token}"},
        params={"limit": limit, "offset": offset},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    respuesta = response.json()
    if "total" not in respuesta or "items" not in respuesta:
        raise ResponseJSONError("Error en la respuesta, falta el total o el items")
    return respuesta["total"], respuesta["items"]


@sleep_and_retry
@limits(calls=LLAMADOS_CANTIDAD, period=CUATRO_SEGUNDOS)
def get_historial_puestos(base_url, token, persona_id):
    """Consultar historial de puestos, entrega un elemento (el mas reciente) de encontrarse"""
    response = requests.get(
        url=f"{base_url}/v1/historial_puestos",
        headers={"authorization": f"Bearer {token}"},
        params={"persona_id": persona_id, "limit": 1, "offset": 0},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    respuesta = response.json()
    if "total" not in respuesta or "items" not in respuesta:
        raise ResponseJSONError("Error en la respuesta, falta el total o el items")
    if respuesta["total"] > 0:
        return respuesta["items"][0]  # Entrega el unico elemento del listado
    return None


def main():
    """Procedimiento principal"""
    base_url = os.getenv("RRHH_PERSONAL_API_URL", None)
    username = os.getenv("RRHH_PERSONAL_API_USERNAME", None)
    password = os.getenv("RRHH_PERSONAL_API_PASSWORD", None)
    try:
        token = get_token(base_url, username, password)
        limit = 10
        offset = 0
        total = None
        while True:
            total, personas = get_personas(base_url, token, limit, offset)
            print(f"Voy en el offset {offset} de {total}...")
            datos = []
            for persona in personas:
                nombre = f"{persona['nombres']} {persona['apellido_primero']} {persona['apellido_segundo']}"
                centro_trabajo_clave = None
                historial_puesto = get_historial_puestos(base_url, token, persona["id"])
                if historial_puesto:
                    centro_trabajo_clave = historial_puesto["centro_trabajo"]
                datos.append([nombre, centro_trabajo_clave])
            print(tabulate(datos, headers=["Nombre", "Centro de Trabajo"]))
            offset += limit
            if offset >= total:
                break
    except requests.ConnectionError as error:
        print(f"Error de conexion: {error}")
    except requests.Timeout as error:
        print(f"Error de falta de respuesta a tiempo: {error}")
    except (ConfigurationError, ResponseJSONError, StatusCodeNot200Error) as error:
        print(error)
    return


if __name__ == "__main__":
    main()
