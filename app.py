import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE SEGURIDAD Y LIMPIEZA ---
st.set_page_config(page_title="OmniContable VE", layout="wide", initial_sidebar_state="expanded")

# Ocultar menús de Streamlit para evitar navegación externa
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# --- 1. INICIALIZACIÓN DE MEMORIA (BASE DE DATOS) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'usuarios': {'admin@omni.com': {'pass': make_hashes('admin123'), 'rol': 'ADMIN', 'rif': 'MASTER'}},
        'empresas': {} # Aquí se guardarán todos tus clientes
    }
# --- BASE DE DATOS LOCAL (SIMULADA) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'usuarios': {
            'admin@omni.com': {'pass': make_hashes('admin123'), 'rol': 'ADMIN', 'rif': 'MASTER'}
        },
        'empresas': {
            'J500773587': {
                'nombre': "BALY'S TODO EN UNO C.A.", 
                'vence': (datetime.now() + timedelta(days=4)).date(), 
                'estado': 'Habilitado'
            }
        }
    }

# --- CONTROL DE ACCESO ---
if 'auth' not in st.session_state:
    st.title("🔐 Acceso al Sistema OmniContable VE")
    with st.form("login_form"):
        u = st.text_input("Usuario (Correo)")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            if u in st.session_state.db['usuarios'] and check_hashes(p, st.session_state.db['usuarios'][u]['pass']):
                st.session_state.auth = True
                st.session_state.user = u
                st.session_state.rol = st.session_state.db['usuarios'][u]['rol']
                st.session_state.rif = st.session_state.db['usuarios'][u].get('rif')
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    st.stop()

# --- BARRA LATERAL (SALIDA RÁPIDA) ---
if st.sidebar.button("🚪 Salida Rápida (Cerrar Sesión)"):
    st.session_state.clear()
    st.rerun()

# --- 3. PANEL DE ADMINISTRADOR (CONTROL MAESTRO) ---
if st.session_state.rol == "ADMIN":
    st.title("👑 Consola de Administración Global")
    st.sidebar.button("🚪 Salida Rápida", on_click=lambda: st.session_state.clear())
    
    tab1, tab2, tab3 = st.tabs(["📊 Listado de Clientes", "🏢 Registrar Nueva Empresa", "👤 Usuarios Adicionales"])
    
    with tab1:
        st.subheader("📊 Control de Clientes y Pagos")
        if not st.session_state.db['empresas']:
            st.info("No hay empresas registradas.")
        else:
            # Encabezado de tabla
            h1, h2, h3, h4 = st.columns([2, 3, 2, 2])
            h1.write("**RIF**")
            h2.write("**Empresa**")
            h3.write("**Estado**")
            h4.write("**Acción**")
            st.divider()

            for rif, info in st.session_state.db['empresas'].items():
                c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
                c1.write(rif)
                c2.write(info['nombre'])
                
                # Color por estado
                color = "green" if info['estado'] == "Habilitado" else "red"
                c3.markdown(f":{color}[{info['estado']}]")
                
                # Botón de Suspensión por falta de pago
                btn_label = "🚫 Suspender" if info['estado'] == "Habilitado" else "✅ Activar"
                if c4.button(btn_label, key=f"pago_{rif}"):
                    nuevo = "Deshabilitado" if info['estado'] == "Habilitado" else "Habilitado"
                    st.session_state.db['empresas'][rif]['estado'] = nuevo
                    st.rerun()

    with tab2:
        st.subheader("➕ Alta de Nueva Empresa")
        with st.form("registro_maestro_final"):
            e_rif = st.text_input("RIF (Ej: J500773587)")
            e_nom = st.text_input("Razón Social")
            e_vence = st.date_input("Vencimiento de Suscripción")
            st.divider()
            e_mail = st.text_input("Email del Cliente")
            e_pass = st.text_input("Contraseña del Cliente", type="password")
            
            # El botón ahora está DENTRO del formulario
            if st.form_submit_button("Habilitar Empresa y Cliente"):
                # Guardar en memoria
                st.session_state.db['empresas'][e_rif] = {
                    'nombre': e_nom, 
                    'vence': e_vence, 
                    'estado': 'Habilitado'
                }
                st.session_state.db['usuarios'][e_mail] = {
                    'pass': make_hashes(e_pass), 
                    'rol': 'CLIENTE', 
                    'rif': e_rif
                }
                st.success(f"✅ ¡{e_nom} registrada!")
                st.rerun()

    with tab3:
        st.subheader("👤 Usuarios Extras")
        with st.form("extra_user_form"):
            target = st.selectbox("Seleccione Empresa", list(st.session_state.db['empresas'].keys()))
            u_mail = st.text_input("Email Adicional")
            u_pass = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Vincular Acceso"):
                st.session_state.db['usuarios'][u_mail] = {'pass': make_hashes(u_pass), 'rol': 'CLIENTE', 'rif': target}
                st.success("Acceso concedido.")

# --- 4. PANEL DE CLIENTE (VISTA LIMITADA) ---
else:
    rif_cliente = st.session_state.rif
    if rif_cliente in st.session_state.db['empresas']:
        empresa_info = st.session_state.db['empresas'][rif_cliente]
        
        # VERIFICACIÓN DE PAGO/ESTADO
        if empresa_info['estado'] == "Deshabilitado":
            st.error("🚫 Su acceso ha sido suspendido. Por favor, contacte al administrador.")
            st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.clear())
            st.stop() # Bloquea el resto del sistema
            
        st.title(f"🏢 {empresa_info['nombre']}")
        st.sidebar.button("🚪 Salida Rápida", on_click=lambda: st.session_state.clear())
        st.write("Bienvenido a su Sistema Contable.")
    else:
        st.error("Empresa no encontrada.")
        st.stop()

# --- VISTA CLIENTE ---
else:
    usuario = st.session_state.usuario
    info = st.session_state.db['empresas'][rif]
    
    # Alerta 5 días antes
    dias_vence = (info['vence'] - datetime.now().date()).days
    if 0 <= dias_vence <= 5:
        st.warning(f"⚠️ Alerta: Su suscripción vence en {dias_vence} días ({info['vence']}).")

    st.title(f"🏢 Panel Contable: {info['nombre']}")
    menu = st.sidebar.radio("Módulos", ["🔍 Lupa de Historial", "📊 Ganancias y Pérdidas", "🏛️ Fiscal / SENIAT", "⚙️ Ajuste Inflación"])

    if menu == "🔍 Lupa de Historial":
        st.subheader("Búsqueda en Big Data (100,000+ Archivos)")
        st.text_input("Buscar por Factura N°, RIF, Concepto o Monto...")
        st.info("Mostrando últimos registros sincronizados por OCR...")

    elif menu == "📊 Ganancias y Pérdidas":
        st.subheader("Estado de Resultados (Comparativa Divisas)")
        tasa = st.number_input("Tasa BCV", value=36.50)
        st.table({
            "Concepto": ["Ingresos Operativos", "Costo de Ventas", "Utilidad Bruta"],
            "Monto Bs": [150000.00, 45000.00, 105000.00],
            "Monto USD": [150000/tasa, 45000/tasa, 105000/tasa]
        })
