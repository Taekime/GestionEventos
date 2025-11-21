import sqlite3
import hashlib 
from abc import ABC, abstractmethod
from excepciones import EventoNoEncontradoError, CuposAgotadosError, DatosInvalidosError, TopeHorarioError
from validador_evento import ValidadorEvento

class ServicioNotificacion(ABC):
    @abstractmethod
    def enviar(self, destinatario, mensaje):
        pass

class RepositorioEventos:
    def __init__(self, db_name="universidad.db"):
        self.db_name = db_name
        self.validador = ValidadorEvento() 
        self._inicializar_db()

    def _conectar(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON") 
        return conn

    def _inicializar_db(self):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    hora TEXT NOT NULL,
                    cupos INTEGER NOT NULL,
                    foto TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inscripciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evento_id INTEGER,
                    email_estudiante TEXT,
                    FOREIGN KEY(evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
                    UNIQUE(evento_id, email_estudiante)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    nombre TEXT
                )
            ''')
            conn.commit()

    # --- MÉTODOS DE EVENTOS ---
    def guardar(self, evento: dict):
        if not self.validador.validar_nombre(evento.get("nombre", "")):
            raise DatosInvalidosError("Nombre inválido")
        if not self.validador.validar_descripcion(evento.get("descripcion", "")):
            raise DatosInvalidosError("Descripción obligatoria")
        if not self.validador.validar_cupos(evento.get("cupos", 0)):
            raise DatosInvalidosError("Cupos inválidos")
        if not self.validador.validar_fecha_futura(evento.get("fecha", "")):
            raise DatosInvalidosError("La fecha debe ser futura y en formato YYYY-MM-DD")

        foto = evento.get("foto", "").strip()
        if not foto:
            foto = "https://img.icons8.com/clouds/200/000000/calendar.png"

        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO eventos (nombre, descripcion, fecha, hora, cupos, foto) VALUES (?, ?, ?, ?, ?, ?)",
                (evento["nombre"], evento["descripcion"], evento["fecha"], evento["hora"], evento["cupos"], foto)
            )
            conn.commit()

    def obtener_todos(self):
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM eventos ORDER BY fecha ASC")
            return [dict(row) for row in cursor.fetchall()]

    def buscar_eventos_filtro(self, termino):
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            sql = "SELECT * FROM eventos WHERE nombre LIKE ? OR descripcion LIKE ? ORDER BY fecha ASC"
            parametro = f"%{termino}%"
            cursor.execute(sql, (parametro, parametro))
            return [dict(row) for row in cursor.fetchall()]

    def buscar_por_nombre(self, nombre):
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM eventos WHERE nombre = ?", (nombre,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def eliminar_evento(self, nombre):
        evento = self.buscar_por_nombre(nombre)
        if not evento:
            raise EventoNoEncontradoError(f"No se puede borrar: '{nombre}' no existe.")
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM eventos WHERE id = ?", (evento["id"],))
            conn.commit()

    def modificar_evento(self, nombre_original, nuevos_datos):
        evento = self.buscar_por_nombre(nombre_original)
        if not evento:
            raise EventoNoEncontradoError(f"No se encontró el evento '{nombre_original}' para editar.")

        nombre = nuevos_datos.get("nombre") or evento["nombre"]
        desc = nuevos_datos.get("descripcion") or evento["descripcion"]
        fecha = nuevos_datos.get("fecha") or evento["fecha"]
        hora = nuevos_datos.get("hora") or evento["hora"]
        foto = nuevos_datos.get("foto") or evento["foto"]
        
        nuevos_cupos = nuevos_datos.get("cupos")
        if nuevos_cupos and str(nuevos_cupos).isdigit():
            cupos = int(nuevos_cupos)
        else:
            cupos = evento["cupos"]

        if nuevos_datos.get("fecha") and not self.validador.validar_fecha_futura(fecha):
             raise DatosInvalidosError("La nueva fecha no puede ser en el pasado.")

        with self._conectar() as conn:
            cursor = conn.cursor()
            sql = '''
                UPDATE eventos 
                SET nombre=?, descripcion=?, fecha=?, hora=?, cupos=?, foto=?
                WHERE id=?
            '''
            cursor.execute(sql, (nombre, desc, fecha, hora, cupos, foto, evento["id"]))
            conn.commit()

    def contar_inscritos(self, evento_id):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inscripciones WHERE evento_id = ?", (evento_id,))
            return cursor.fetchone()[0]

    # --- MEJORA: OBTENER NOMBRE Y EMAIL ---
    def obtener_inscritos_lista(self, evento_id):
        """Retorna lista de tuplas (Nombre, Email)"""
        with self._conectar() as conn:
            cursor = conn.cursor()
            # JOIN con tabla usuarios para sacar el nombre real
            sql = '''
                SELECT u.nombre, i.email_estudiante 
                FROM inscripciones i
                JOIN usuarios u ON i.email_estudiante = u.email
                WHERE i.evento_id = ?
            '''
            cursor.execute(sql, (evento_id,))
            return cursor.fetchall()

    def obtener_eventos_estudiante(self, email):
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            sql = '''
                SELECT e.* FROM eventos e
                INNER JOIN inscripciones i ON e.id = i.evento_id
                WHERE i.email_estudiante = ?
                ORDER BY e.fecha ASC
            '''
            cursor.execute(sql, (email,))
            return [dict(row) for row in cursor.fetchall()]

    # --- MÉTODOS DE AUTENTICACIÓN ---
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def registrar_estudiante(self, email, password, nombre):
        if not ValidadorEvento.validar_email(email):
             raise DatosInvalidosError("Debe usar un correo institucional (@pregrado.ubo.cl)")
        if len(password) < 4:
            raise DatosInvalidosError("La contraseña es muy corta.")

        pass_hash = self._hash_password(password)
        
        try:
            with self._conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO usuarios (email, password_hash, nombre) VALUES (?, ?, ?)", 
                               (email, pass_hash, nombre))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            raise DatosInvalidosError("Este correo ya está registrado.")

    def autenticar_estudiante(self, email, password):
        pass_hash = self._hash_password(password)
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE email = ? AND password_hash = ?", (email, pass_hash))
            usuario = cursor.fetchone()
            return dict(usuario) if usuario else None

    def cambiar_password(self, email, password_actual, password_nueva):
        usuario = self.autenticar_estudiante(email, password_actual)
        if not usuario:
            raise DatosInvalidosError("La contraseña actual es incorrecta.")
        
        if len(password_nueva) < 4:
            raise DatosInvalidosError("La nueva contraseña es muy corta.")

        nuevo_hash = self._hash_password(password_nueva)
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET password_hash = ? WHERE email = ?", (nuevo_hash, email))
            conn.commit()

class ServicioInscripcion:
    def __init__(self, repositorio: RepositorioEventos, notificador: ServicioNotificacion):
        self._repo = repositorio
        self._notificador = notificador

    def inscribir_estudiante(self, nombre_evento, email_estudiante):
        evento = self._repo.buscar_por_nombre(nombre_evento)
        if not evento:
            raise EventoNoEncontradoError(f"El evento '{nombre_evento}' no existe.")

        evento_id = evento["id"]
        cupos_totales = evento["cupos"]
        inscritos_actuales = self._repo.contar_inscritos(evento_id)

        if inscritos_actuales >= cupos_totales:
            raise CuposAgotadosError(f"No quedan cupos para '{nombre_evento}'")

        mis_eventos = self._repo.obtener_eventos_estudiante(email_estudiante)
        for ev in mis_eventos:
            if ev['fecha'] == evento['fecha'] and ev['hora'] == evento['hora']:
                raise TopeHorarioError(f"Conflicto de horario con '{ev['nombre']}' (Ambos son el {ev['fecha']} a las {ev['hora']})")

        try:
            with self._repo._conectar() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO inscripciones (evento_id, email_estudiante) VALUES (?, ?)",
                    (evento_id, email_estudiante)
                )
                conn.commit()
            
            mensaje = f"Inscripción confirmada en '{nombre_evento}' el día {evento['fecha']}"
            try:
                self._notificador.enviar(email_estudiante, mensaje)
            except Exception as e:
                print(f"Advertencia: No se pudo notificar: {e}")

            print(f"✅ {email_estudiante} inscrito correctamente en {nombre_evento}")
            
        except sqlite3.IntegrityError:
            print(f"⚠️ Ya estás inscrito en este evento.")

    def cancelar_inscripcion(self, nombre_evento, email_estudiante):
        evento = self._repo.buscar_por_nombre(nombre_evento)
        if not evento:
            raise EventoNoEncontradoError("Evento no encontrado")
            
        with self._repo._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM inscripciones WHERE evento_id = ? AND email_estudiante = ?",
                (evento["id"], email_estudiante)
            )
            if cursor.rowcount > 0:
                print(f"🗑️ Inscripción cancelada para {email_estudiante}")
                conn.commit()
            else:
                print("❌ No se encontró una inscripción para cancelar.")