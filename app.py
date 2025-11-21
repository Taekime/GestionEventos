import streamlit as st
import datetime
import time
import pandas as pd
from gestion_eventos import RepositorioEventos, ServicioInscripcion, ServicioNotificacion, DatosInvalidosError, TopeHorarioError

# Configuración de la página
st.set_page_config(page_title="Eventos UBO", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS CSS MEJORADOS ---
st.markdown("""
    <style>
    /* Estilo para los botones rojos */
    div[data-testid="stButton"] button[kind="secondary"] {
        background-color: #ff4b4b;
        color: white;
        border: none;
    }
    /* Contenedor de Ticket */
    .ticket-card {
        border-left: 5px solid #ff4b4b;
        background-color: #262730;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CLASES AUXILIARES ---
class NotificadorWeb(ServicioNotificacion):
    def enviar(self, destinatario, mensaje):
        st.toast(f"📧 {destinatario}: {mensaje}", icon="✅")
        return True

# --- INICIALIZACIÓN ---
def inicializar_sistema():
    if 'repositorio' not in st.session_state:
        st.session_state.repositorio = RepositorioEventos()
        st.session_state.notificador = NotificadorWeb()
        st.session_state.inscripcion = ServicioInscripcion(st.session_state.repositorio, st.session_state.notificador)
    if 'usuario' not in st.session_state:
        st.session_state.usuario = None
    if 'rol' not in st.session_state:
        st.session_state.rol = None

inicializar_sistema()
repo = st.session_state.repositorio
servicio = st.session_state.inscripcion

# --- UTILIDADES ---
def formatear_fecha(fecha_str):
    try:
        obj = datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
        return obj.strftime("%d-%m-%Y")
    except: return fecha_str

# --- LOGIN ---
def mostrar_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/User_icon_2.svg/480px-User_icon_2.svg.png", width=80)
            st.markdown("<h2 style='text-align: center;'>Eventos UBO</h2>", unsafe_allow_html=True)
            
            tab1, tab2, tab3 = st.tabs(["🎓 Estudiante", "🔑 Admin", "📝 Registro"])
            
            with tab1:
                with st.form("log_est"):
                    email = st.text_input("Correo", placeholder="alumno@pregrado.ubo.cl")
                    pwd = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("Ingresar", type="primary"):
                        alum = repo.autenticar_estudiante(email, pwd)
                        if alum:
                            st.session_state.usuario = alum
                            st.session_state.rol = "estudiante"
                            st.rerun()
                        else: st.error("Datos incorrectos")

            with tab2:
                with st.form("log_adm"):
                    u = st.text_input("Usuario")
                    p = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("Ingresar"):
                        if u == "admin" and p == "ubo123":
                            st.session_state.usuario = {"nombre": "Admin", "email": "admin@ubo.cl"}
                            st.session_state.rol = "admin"
                            st.rerun()
                        else: st.error("Acceso denegado")

            with tab3:
                with st.form("reg"):
                    # CAMBIO 1: Etiqueta Nombre Completo
                    n = st.text_input("Nombre Completo")
                    e = st.text_input("Correo")
                    p1 = st.text_input("Contraseña", type="password")
                    p2 = st.text_input("Confirmar", type="password")
                    if st.form_submit_button("Registrar"):
                        if p1!=p2: st.error("Claves no coinciden")
                        else:
                            try:
                                repo.registrar_estudiante(e, p1, n)
                                st.success("Registrado! Inicia sesión.")
                            except Exception as ex: st.error(f"{ex}")

# --- INTERFAZ ESTUDIANTE ---
def interfaz_estudiante():
    st.sidebar.markdown(f"### 👤 {st.session_state.usuario['nombre']}")
    menu = st.sidebar.radio("Menú", ["📅 Calendario", "✅ Mis Inscripciones", "🔐 Mi Cuenta"])
    st.sidebar.divider()
    if st.sidebar.button("Salir"):
        st.session_state.usuario = None
        st.session_state.rol = None
        st.rerun()

    if menu == "📅 Calendario":
        st.title("📅 Próximos Eventos")
        col_search, col_void = st.columns([3, 1])
        termino = col_search.text_input("🔍 Buscar evento...", placeholder="Nombre del evento")
        
        if termino: eventos = repo.buscar_eventos_filtro(termino)
        else: eventos = repo.obtener_todos()

        if not eventos: st.info("No hay eventos disponibles.")
        
        for ev in eventos:
            with st.container(border=True):
                # CAMBIO 2: Centrado vertical en la columna del botón
                c1, c2, c3 = st.columns([1, 4, 2], vertical_alignment="center")
                with c1:
                    # CAMBIO 3: HTML para forzar tamaño de imagen (150px altura fija)
                    img_url = ev['foto'] if ev['foto'] else "https://img.icons8.com/clouds/200/000000/calendar.png"
                    st.markdown(f"""
                        <img src="{img_url}" style="width:100%; height:120px; object-fit:cover; border-radius:5px;">
                    """, unsafe_allow_html=True)
                    
                with c2:
                    st.subheader(ev['nombre'])
                    st.caption(f"📅 {formatear_fecha(ev['fecha'])} | ⏰ {ev['hora']} hrs")
                    st.write(ev['descripcion'])
                with c3:
                    ins = repo.contar_inscritos(ev['id'])
                    total = ev['cupos']
                    st.progress(ins/total if total>0 else 1, text=f"{ins}/{total} Cupos")
                    
                    if ins < total:
                        if st.button("Inscribirme", key=f"in_{ev['id']}", type="primary", use_container_width=True):
                            try:
                                servicio.inscribir_estudiante(ev['nombre'], st.session_state.usuario['email'])
                                st.success("Inscrito!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e: st.error(f"{e}")
                    else:
                        st.error("AGOTADO", icon="🚫")

    elif menu == "✅ Mis Inscripciones":
        st.title("🎫 Mis Tickets")
        mis_evs = repo.obtener_eventos_estudiante(st.session_state.usuario['email'])
        
        if not mis_evs:
            st.warning("No tienes inscripciones activas.")
        else:
            for ev in mis_evs:
                with st.container(border=True):
                    # CAMBIO 4: Centrado vertical para el botón cancelar
                    c_date, c_info, c_btn = st.columns([1.5, 4, 1.5], vertical_alignment="center")
                    
                    with c_date:
                        st.markdown(f"<h2 style='text-align:center; color:#ff4b4b; margin:0;'>{ev['fecha'][-2:]}</h2>", unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; margin:0;'>{ev['fecha'][5:7]}/{ev['fecha'][:4]}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; font-weight:bold;'>⏰ {ev['hora']}</p>", unsafe_allow_html=True)

                    with c_info:
                        st.markdown(f"### {ev['nombre']}")
                        st.write(f"_{ev['descripcion']}_")
                        st.caption("✅ Estado: Confirmado")

                    with c_btn:
                        if st.button("Cancelar 🗑️", key=f"del_{ev['id']}", use_container_width=True):
                            servicio.cancelar_inscripcion(ev['nombre'], st.session_state.usuario['email'])
                            st.rerun()

    elif menu == "🔐 Mi Cuenta":
        st.header("Cambiar Contraseña")
        with st.form("pass_ch"):
            a = st.text_input("Actual", type="password")
            n = st.text_input("Nueva", type="password")
            if st.form_submit_button("Guardar"):
                try:
                    repo.cambiar_password(st.session_state.usuario['email'], a, n)
                    st.success("Contraseña cambiada!")
                except Exception as e: st.error(f"{e}")

# --- INTERFAZ ADMIN ---
def interfaz_admin():
    st.sidebar.markdown("## 🛠️ Panel Admin")
    op = st.sidebar.radio("Menú", ["1. Crear Evento", "2. Editar Eventos", "3. Estadísticas y Reportes"])
    st.sidebar.divider()
    if st.sidebar.button("Salir"):
        st.session_state.usuario = None
        st.session_state.rol = None
        st.rerun()

    if op == "1. Crear Evento":
        st.header("➕ Nuevo Evento")
        with st.container(border=True):
            with st.form("new"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nombre del Evento")
                fec = c2.date_input("Fecha", min_value=datetime.date.today())
                hor = c1.time_input("Hora")
                cup = c2.number_input("Cupos", 1, 1000, 20)
                fot = st.text_input("URL Foto")
                des = st.text_area("Descripción")
                if st.form_submit_button("Publicar", type="primary"):
                    try:
                        d = {"nombre": nom, "descripcion": des, "fecha": str(fec), "hora": str(hor), "cupos": cup, "foto": fot}
                        repo.guardar(d)
                        st.success("Creado!")
                    except Exception as e: st.error(f"{e}")

    elif op == "2. Editar Eventos":
        st.header("✏️ Gestión de Eventos")
        lista = repo.obtener_todos()
        if not lista: st.info("No hay eventos para editar.")
        
        for ev in lista:
            with st.expander(f"📅 {ev['fecha']} - {ev['nombre']}"):
                with st.form(f"ed_{ev['id']}"):
                    c1, c2 = st.columns(2)
                    n_nom = c1.text_input("Nombre", value=ev['nombre'])
                    
                    try: f_obj = datetime.datetime.strptime(ev['fecha'], "%Y-%m-%d").date()
                    except: f_obj = datetime.date.today()
                    n_fec = c2.date_input("Fecha", value=f_obj)
                    
                    try: h_obj = datetime.datetime.strptime(ev['hora'], "%H:%M:%S").time()
                    except: 
                        try: h_obj = datetime.datetime.strptime(ev['hora'], "%H:%M").time()
                        except: h_obj = datetime.time(9,0)
                    n_hor = c1.time_input("Hora", value=h_obj)
                    
                    n_cup = c2.number_input("Cupos", value=ev['cupos'], min_value=1)
                    n_fot = st.text_input("URL Foto", value=ev['foto'])
                    n_des = st.text_area("Descripción", value=ev['descripcion'])
                    
                    cols = st.columns(2)
                    if cols[0].form_submit_button("💾 Guardar Cambios", type="primary"):
                        dt = {"nombre": n_nom, "descripcion": n_des, "fecha": str(n_fec), "hora": str(n_hor), "cupos": n_cup, "foto": n_fot}
                        try:
                            repo.modificar_evento(ev['nombre'], dt)
                            st.success("Guardado!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e: st.error(f"{e}")
                
                if st.button("🗑️ Eliminar Evento", key=f"del_{ev['id']}"):
                    repo.eliminar_evento(ev['nombre'])
                    st.rerun()

    elif op == "3. Estadísticas y Reportes":
        st.header("📊 Métricas por Evento")
        lista = repo.obtener_todos()
        if not lista:
            st.warning("Crea eventos primero.")
            st.stop()

        seleccion = st.selectbox("Selecciona un evento para ver sus detalles:", [e['nombre'] for e in lista])
        evento_sel = next((e for e in lista if e['nombre'] == seleccion), None)
        
        if evento_sel:
            inscritos_count = repo.contar_inscritos(evento_sel['id'])
            total_cupos = evento_sel['cupos']
            disponibles = total_cupos - inscritos_count
            pct = round((inscritos_count / total_cupos) * 100, 1)

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Inscritos", inscritos_count)
            m2.metric("Cupos Disponibles", disponibles)
            m3.metric("Porcentaje Ocupación", f"{pct}%")
            
            st.progress(inscritos_count/total_cupos, text=f"{inscritos_count} de {total_cupos} ocupados")
            st.divider()
            
            # CAMBIO 5: Tabla con NOMBRES y Correos
            st.subheader(f"📋 Lista de Asistentes: {seleccion}")
            # Esta función ahora devuelve una lista de tuplas (Nombre, Email)
            lista_datos = repo.obtener_inscritos_lista(evento_sel['id'])
            
            if lista_datos:
                # Creamos el DataFrame con dos columnas claras
                df = pd.DataFrame(lista_datos, columns=["Nombre Alumno", "Correo Institucional"])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aún no hay inscritos en este evento.")

            st.divider()
            if st.button(f"📥 Descargar CSV de {seleccion}", type="primary"):
                from servicios.servicio_reportes import ServicioReportes
                srv = ServicioReportes(repo)
                try:
                    srv.exportar_lista_csv(seleccion)
                    st.success(f"Archivo generado exitosamente en la carpeta del proyecto.")
                except Exception as e: st.error(f"{e}")

# --- MAIN ---
if st.session_state.usuario is None:
    mostrar_login()
elif st.session_state.rol == "admin":
    interfaz_admin()
else:
    interfaz_estudiante()