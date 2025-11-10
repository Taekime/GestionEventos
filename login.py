# login.py (refactorizado - correcciones de seguridad)
import sqlite3
import subprocess
import os
import hashlib
import getpass
from typing import Optional

DB_PATH = "users.db"

def hash_password(password: str) -> str:
    """Hash simple con SHA-256 (usar bcrypt en producción)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def inicializar_db():
    """Crea una DB simple con usuarios (almacena hashes, no contraseñas en claro)."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT)"
        )
        # Insertar un usuario de prueba con password hasheada (si no existe)
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("user1", hash_password("password1"))
            )
        except sqlite3.IntegrityError:
            pass
        conn.commit()

def cargar_credenciales_admin() -> Optional[tuple]:
    """
    Cargar credenciales admin desde variables de entorno (no hardcodeadas).
    Retorna (username, password_hash) o None si no están definidas.
    """
    admin_user = os.getenv("ADMIN_USERNAME")
    admin_pass = os.getenv("ADMIN_PASSWORD")  # si se usa, preferible guardar HASH en secrets manager
    if not admin_user or not admin_pass:
        return None
    return (admin_user, hash_password(admin_pass))

def login(username: str, password: str) -> bool:
    """
    Autentica al usuario usando consultas parametrizadas (evita inyección SQL)
    y comparando hashes de contraseña.
    """
    # Comprobar admin usando variables de entorno (si están definidas)
    admin = cargar_credenciales_admin()
    if admin is not None:
        admin_user, admin_hash = admin
        if username == admin_user and hash_password(password) == admin_hash:
            print("Login exitoso: Admin")
            return True

    # Uso de query parametrizada para evitar SQL injection
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = cur.fetchone()

    if row and row[0] == hash_password(password):
        print("Login exitoso")
        return True

    print("Credenciales inválidas")
    return False

# Lista blanca de comandos permitidos y su forma segura (sin shell=True)
_COMANDOS_PERMITIDOS = {
    "whoami": ["whoami"],
    "uname": ["uname", "-a"],
    "uptime": ["uptime"],
    "ls": ["ls", "-l"],  # si se necesita permitir paths, validarlo explícitamente
}

def recuperar_info_adicional(comando_clave: str) -> str:
    """
    Ejecuta un comando seguro elegido de una lista blanca.
    'comando_clave' debe ser una clave conocida (por ejemplo 'whoami', 'uname').
    """
    if comando_clave not in _COMANDOS_PERMITIDOS:
        raise ValueError("Comando no permitido")

    args = _COMANDOS_PERMITIDOS[comando_clave]
    # Ejecutar sin shell (shell=False) usando lista de args
    resultado = subprocess.run(args, shell=False, capture_output=True, text=True, check=False)
    return resultado.stdout.strip()

if __name__ == "__main__":
    # Preparar DB
    inicializar_db()

    # Ejemplo de uso (uso getpass para no mostrar la contraseña)
    user = input("Usuario: ")
    pwd = getpass.getpass("Password: ")

    if login(user, pwd):
        admin = cargar_credenciales_admin()
        # Si las credenciales admin están definidas, permitir info adicional mediante lista blanca
        if admin is not None and user == admin[0]:
            print("Comandos disponibles:", ", ".join(_COMANDOS_PERMITIDOS.keys()))
            cmd_key = input("Ingrese clave de comando permitido para ver info del sistema: ").strip()
            try:
                salida = recuperar_info_adicional(cmd_key)
                print("Salida del comando:")
                print(salida)
            except ValueError as e:
                print("Operación no permitida:", e)
    else:
        # comportamiento en caso de fallo (no revelar detalles)
        pass
