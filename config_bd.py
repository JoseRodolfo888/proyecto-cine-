import os
from pathlib import Path


def cargar_env():
    """Carga variables desde el archivo .env ubicado junto a este script."""
    ruta_env = Path(__file__).resolve().parent / ".env"
    if not ruta_env.exists():
        return

    for linea in ruta_env.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        clave = clave.strip()
        valor = valor.strip().strip('"').strip("'")
        os.environ.setdefault(clave, valor)


def obtener_config_bd():
    """Devuelve los parámetros de conexión a MySQL."""
    cargar_env()
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "cine"),
    }