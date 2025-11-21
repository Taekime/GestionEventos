import sys
import os
import getpass
from datetime import datetime 
from excepciones import EventoNoEncontradoError, CuposAgotadosError, DatosInvalidosError, TopeHorarioError
from logger import Logger
from servicios.notificador_sms import NotificadorSMS
from servicios.servicio_reportes import ServicioReportes
from gestion_eventos import RepositorioEventos, ServicioInscripcion

# --- CREDENCIALES ADMIN ---
ADMIN_USER = "admin"
ADMIN_PASS = "ubo123" 

# --- UTILIDADES ---
def limpiar_pantalla():
    if os.name == 'nt': os.system('cls')
    else: os.system('clear')

def pausar():
    input("\n👉 Presione [Enter] para continuar...")

def formatear_fecha_chile(fecha_str):
    try:
        obj_fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        return obj_fecha.strftime("%d-%m-%Y")
    except: return fecha_str 

# --- MENÚS ---
def mostrar_login_principal():
    limpiar_pantalla()
    print("\n🔹 ===== BIENVENIDO AL SISTEMA DE EVENTOS UBO ===== 🔹")
    print("1. Soy ADMINISTRADOR")
    print("2. Soy ESTUDIANTE")
    print("3. Salir")
    return input("Seleccione su rol: ")

def mostrar_submenu_estudiante():
    limpiar_pantalla()
    print("\n🎓 --- ACCESO ESTUDIANTES ---")
    print("1. Iniciar Sesión")
    print("2. Registrarme (Crear cuenta)")
    print("3. Volver atrás")
    return input("Elija una acción: ")

def mostrar_menu_admin():
    limpiar_pantalla()
    print("\n🔑 --- PANEL DE ADMINISTRADOR ---")
    print("1. Crear nuevo evento")
    print("2. Ver todos los eventos")
    print("3. Modificar evento existente") 
    print("4. Eliminar evento")
    print("5. Exportar lista de asistencia (Excel/CSV)")
    print("6. Generar reporte en consola")
    print("7. Cerrar sesión")
    return input("Elija una acción: ")

def mostrar_panel_estudiante(nombre_alumno):
    limpiar_pantalla()
    print(f"\n🎓 --- Hola, {nombre_alumno} ---")
    print("1. Ver TODOS los eventos (Calendario)")
    print("2. Ver MIS inscripciones")
    print("3. Inscribirse a un evento")
    print("4. Cancelar mi inscripción")
    print("5. Cerrar sesión")
    return input("Elija una acción: ")

def main():
    logger = Logger()
    repositorio = RepositorioEventos()
    notificador = NotificadorSMS(logger)
    inscripcion = ServicioInscripcion(repositorio, notificador)
    reportes = ServicioReportes(repositorio)

    rol_actual = None 
    usuario_actual_email = None
    usuario_actual_nombre = None

    while True:
        if rol_actual is None:
            opcion = mostrar_login_principal()
            
            # --- LOGIN ADMIN ---
            if opcion == "1":
                print("\n🔐 Autenticación Admin")
                while True:
                    user_input = input("Usuario (o 's' para salir): ")
                    if user_input.lower() == 's': break
                    try: pass_input = getpass.getpass("Contraseña: ")
                    except: pass_input = input("Contraseña: ")

                    if user_input == ADMIN_USER and pass_input == ADMIN_PASS:
                        rol_actual = "admin"
                        print("✅ Acceso concedido.")
                        break 
                    else: print("❌ Credenciales incorrectas.")

            # --- FLUJO ESTUDIANTE ---
            elif opcion == "2":
                sub_opcion = mostrar_submenu_estudiante()
                
                if sub_opcion == "1": # LOGIN
                    print("\n🎓 Iniciar Sesión")
                    while True:
                        email = input("Correo (o 's' para salir): ")
                        if email.lower() == 's': break
                        try: pwd = getpass.getpass("Contraseña: ")
                        except: pwd = input("Contraseña: ")
                        
                        alumno = repositorio.autenticar_estudiante(email, pwd)
                        if alumno:
                            rol_actual = "estudiante"
                            usuario_actual_email = alumno["email"]
                            usuario_actual_nombre = alumno["nombre"]
                            break 
                        else: print("❌ Correo o contraseña incorrectos.")

                elif sub_opcion == "2": # REGISTRO
                    print("\n📝 Registro de Nuevo Estudiante")
                    nombre = input("Nombre completo (o 's' para salir): ")
                    if nombre.lower() == 's': continue 
                    email = input("Correo institucional (@pregrado.ubo.cl): ")
                    if email.lower() == 's': continue

                    pwd_valida = False
                    while not pwd_valida:
                        print("\n--- Creación de Contraseña ---")
                        print("Requisito: Mínimo 4 caracteres.")
                        try: 
                            pwd1 = getpass.getpass("Crea tu contraseña: ")
                            pwd2 = getpass.getpass("Repite tu contraseña: ")
                        except:
                            pwd1 = input("Crea tu contraseña: ")
                            pwd2 = input("Repite tu contraseña: ")
                        
                        if pwd1 != pwd2: print("❌ Las contraseñas no coinciden.")
                        elif len(pwd1) < 4: print("❌ La contraseña es muy corta.")
                        else:
                            try:
                                repositorio.registrar_estudiante(email, pwd1, nombre)
                                print("✅ ¡Cuenta creada! Inicia sesión.")
                                pausar()
                                pwd_valida = True 
                            except DatosInvalidosError as e:
                                print(f"❌ Error: {e}")
                                pausar()
                                pwd_valida = True 
                elif sub_opcion == "3": pass 

            elif opcion == "3":
                print("👋 ¡Hasta luego!")
                sys.exit()
            else:
                print("❗ Opción no válida.")
                pausar()
        
        # --- MENÚ INTERNO ADMIN ---
        elif rol_actual == "admin":
            opcion = mostrar_menu_admin()
            
            if opcion == "1": # Crear
                print("\n--- Nuevo Evento ---")
                nombre = input("Nombre: ")
                descripcion = input("Descripción: ")
                print("Nota: Ingrese fecha futura (Ej: 2025-12-30)")
                fecha = input("Fecha (YYYY-MM-DD): ")
                hora = input("Hora (HH:MM): ")
                cupos_str = input("Cupos: ")
                foto = input("URL de foto (Enter para usar default): ")
                try:
                    cupos = int(cupos_str) if cupos_str.isdigit() else 0
                    evento = {"nombre": nombre, "descripcion": descripcion, "fecha": fecha, "hora": hora, "cupos": cupos, "foto": foto}
                    repositorio.guardar(evento)
                    print("✅ Evento creado.")
                except Exception as e: print(f"❌ Error: {e}")
                pausar()

            elif opcion == "2": # Ver todos
                limpiar_pantalla()
                print("\n--- Eventos Registrados ---")
                eventos = repositorio.obtener_todos()
                if eventos:
                    print(f"{'NOMBRE':<20} | {'FECHA':<12} | {'HORA':<6} | {'CUPOS'}")
                    print("-" * 55)
                    for ev in eventos: 
                        fecha_cl = formatear_fecha_chile(ev['fecha'])
                        print(f"{ev['nombre']:<20} | {fecha_cl:<12} | {ev['hora']:<6} | {ev['cupos']}")
                else: print("📭 No hay eventos.")
                pausar()

            elif opcion == "3": # Modificar
                print("\n📝 --- Modificar Evento ---")
                nombre_orig = input("Nombre del evento a editar: ")
                if repositorio.buscar_por_nombre(nombre_orig):
                    print("👇 Ingrese nuevos datos (Enter para mantener actual)")
                    nuevo_nombre = input("Nuevo Nombre: ")
                    nueva_desc = input("Nueva Descripción: ")
                    nueva_fecha = input("Nueva Fecha (YYYY-MM-DD): ")
                    nueva_hora = input("Nueva Hora: ")
                    nuevos_cupos = input("Nuevos Cupos: ")
                    nueva_foto = input("Nueva Foto URL: ")

                    datos = {"nombre": nuevo_nombre, "descripcion": nueva_desc, "fecha": nueva_fecha, "hora": nueva_hora, "cupos": nuevos_cupos, "foto": nueva_foto}
                    try:
                        repositorio.modificar_evento(nombre_orig, datos)
                        print("✅ Evento actualizado.")
                    except Exception as e: print(f"❌ Error: {e}")
                else: print("❌ El evento no existe.")
                pausar()

            elif opcion == "4": # Eliminar
                nombre = input("\nNombre del evento a eliminar: ")
                if input("¿Seguro? (s/n): ").lower() == 's':
                    try:
                        repositorio.eliminar_evento(nombre)
                        print("🗑️ Evento eliminado.")
                    except Exception as e: print(f"❌ {e}")
                pausar()

            elif opcion == "5": # Exportar
                nombre = input("\nNombre del evento: ")
                try: reportes.exportar_lista_csv(nombre)
                except Exception as e: print(f"❌ {e}")
                pausar()

            elif opcion == "6": # Reporte
                nombre = input("\nNombre del evento: ")
                try: reportes.generar_reporte_participacion(nombre)
                except Exception as e: print(f"❌ {e}")
                pausar()

            elif opcion == "7": # Logout
                rol_actual = None

            else:
                print("❗ Opción no válida.")
                pausar()

        # --- MENÚ INTERNO ESTUDIANTE ---
        elif rol_actual == "estudiante":
            opcion = mostrar_panel_estudiante(usuario_actual_nombre)

            if opcion == "1": # Calendario
                limpiar_pantalla()
                print("\n🗓️  --- CALENDARIO DE EVENTOS DISPONIBLES ---")
                eventos = repositorio.obtener_todos()
                if eventos:
                    for ev in eventos:
                        total = ev['cupos']
                        ocupados = repositorio.contar_inscritos(ev['id'])
                        disponibles = total - ocupados
                        porcentaje = int((ocupados / total) * 100) if total > 0 else 0
                        bloques = int(porcentaje / 10)
                        barra = "█" * bloques + "░" * (10 - bloques)

                        fecha_cl = formatear_fecha_chile(ev['fecha'])
                        print(f"📅 {fecha_cl}  |  ⏰ {ev['hora']} hrs")
                        print(f"📌 {ev['nombre']}")
                        print(f"📝 {ev['descripcion']}")
                        print(f"👥 Cupos: [{barra}] {ocupados}/{total} ocupados")
                        
                        if disponibles == 0: print("🔴 AGOTADO")
                        else: print(f"🟢 Quedan {disponibles} lugares")
                        print("-" * 45)
                else: print("📭 No hay eventos disponibles.")
                pausar()

            elif opcion == "2": # Mis Inscripciones
                limpiar_pantalla()
                print(f"\n✅ --- MIS INSCRIPCIONES ({usuario_actual_email}) ---")
                mis_eventos = repositorio.obtener_eventos_estudiante(usuario_actual_email)
                if mis_eventos:
                    print(f"Estás inscrito en {len(mis_eventos)} eventos:\n")
                    for ev in mis_eventos:
                        fecha_cl = formatear_fecha_chile(ev['fecha'])
                        print(f"🔹 {ev['nombre']}")
                        print(f"   📅 {fecha_cl} a las {ev['hora']} hrs")
                        print("-" * 30)
                else: print("📭 No estás inscrito en ningún evento.")
                pausar()

            elif opcion == "3": # Inscribir
                nombre = input("\nNombre del evento: ")
                try: 
                    inscripcion.inscribir_estudiante(nombre, usuario_actual_email)
                except (EventoNoEncontradoError, CuposAgotadosError, DatosInvalidosError, TopeHorarioError) as e:
                    print(f"❌ Error: {e}")
                except Exception as e: 
                    print(f"❌ Error inesperado: {e}")
                pausar()

            elif opcion == "4": # Cancelar
                nombre = input("\nNombre del evento: ")
                try: inscripcion.cancelar_inscripcion(nombre, usuario_actual_email)
                except Exception as e: print(f"❌ {e}")
                pausar()

            elif opcion == "5": # Logout
                rol_actual = None
                usuario_actual_email = None
                usuario_actual_nombre = None
            else:
                print("❗ Opción no válida.")
                pausar()

if __name__ == "__main__":
    main()