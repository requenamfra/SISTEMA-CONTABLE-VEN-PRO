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

# --- INICIALIZACIÓN DE MEMORIA ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'usuarios': {'admin@omni.com': {'pass': make_hashes('admin123'), 'rol': 'ADMIN', 'rif': 'MASTER'}},
        'empresas': {} # Aquí se guardarán los 10.000+ clientes
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

# --- 3. PANEL DE ADMINISTRADOR (CONTROL TOTAL) ---
if st.session_state.rol == "ADMIN":
    st.title("👑 Consola de Administración Global")
    
    # Aquí creamos las 3 pestañas necesarias
    tab1, tab2, tab3 = st.tabs(["📊 Listado de Clientes", "🏢 Registrar Nueva Empresa", "👤 Usuarios Adicionales"])
    
    with tab1:
        st.subheader("📊 Control Maestro de Clientes")
        if not st.session_state.db['empresas']:
            st.info("No hay clientes registrados aún.")
        else:
            for rif, info in st.session_state.db['empresas'].items():
                col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
                with col1:
                    st.write(f"**{rif}**")
                with col2:
                    st.write(info['nombre'])
                with col3:
                    color = "green" if info['estado'] == "Habilitado" else "red"
                    st.markdown(f":{color}[{info['estado']}]")
                with col4:
                    # BOTÓN DE ACCIÓN (Habilitar/Deshabilitar)
                    label = "🚫 Deshabilitar" if info['estado'] == "Habilitado" else "✅ Habilitar"
                    if st.button(label, key=f"btn_{rif}"):
                        nuevo_estado = "Deshabilitado" if info['estado'] == "Habilitado" else "Habilitado"
                        st.session_state.db['empresas'][rif]['estado'] = nuevo_estado
                        st.rerun()
                st.divider()

    if st.form_submit_button("Dar de Alta Empresa y Cliente"):
                # Esto guarda permanentemente en la sesión actual
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
                st.success(f"✅ Registrada: {e_nom}")
                st.rerun() # Esto hace que aparezca en la lista inmediatamente
    with tab3:
        st.subheader("👤 Vincular Usuarios Extras a Empresa Existente")
        with st.form("registro_usuario_extra"):
            target = st.selectbox("Seleccione Empresa Destino", list(st.session_state.db['empresas'].keys()))
            u_mail = st.text_input("Correo del Usuario Adicional")
            u_pass = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Habilitar Acceso Adicional"):
                st.session_state.db['usuarios'][u_mail] = {'pass': make_hashes(u_pass), 'rol': 'CLIENTE', 'rif': target}
                st.success(f"👤 Usuario adicional agregado correctamente.")

# --- VISTA CLIENTE ---
else:
    rif = st.session_state.rif
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
