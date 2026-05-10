import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN E INTERFAZ PRIVADA ---
st.set_page_config(page_title="OmniContable VE", layout="wide")

# OCULTAR MENÚS DE STREAMLIT (Para que no entren a otros sitios)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# --- 2. BASE DE DATOS CON MEMORIA (Sincronizada) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'usuarios': {
            'admin': {'pass': make_hashes('admin123'), 'rol': 'ADMIN'}
        },
        'clientes': {
            'maria': {
                'pass': make_hashes('123'), 
                'vence': datetime.now().date() + timedelta(days=30), 
                'estado': 'Habilitado'
            }
        }
    }

# --- 3. PANTALLA DE INGRESO ---
if 'auth' not in st.session_state:
    st.title("🛡️ Acceso OmniContable VE")
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            # Verificar en Admin o en Clientes registrados
            if u in st.session_state.db['usuarios'] and check_hashes(p, st.session_state.db['usuarios'][u]['pass']):
                st.session_state.auth, st.session_state.rol, st.session_state.user = True, 'ADMIN', u
                st.rerun()
            elif u in st.session_state.db['clientes'] and check_hashes(p, st.session_state.db['clientes'][u]['pass']):
                cliente = st.session_state.db['clientes'][u]
                if cliente['estado'] == "Habilitado":
                    st.session_state.auth, st.session_state.rol, st.session_state.user = True, 'CLIENTE', u
                    st.rerun()
                else:
                    st.error("Acceso suspendido por falta de pago.")
            else:
                st.error("Credenciales incorrectas")
    st.stop()

# --- 4. PANEL DE ADMINISTRADOR ---
if st.session_state.rol == "ADMIN":
    st.title("👑 Consola de Administración Global")
    st.sidebar.button("🚪 Salida Rápida", on_click=lambda: st.session_state.clear())
    
    tab1, tab2, tab3 = st.tabs(["📊 Lista de Clientes", "➕ Registro Nuevo", "👥 Usuarios Adicionales"])
    
    with tab1:
        st.subheader("Control de Suscripciones (Escalable 100k+)")
        if not st.session_state.db['clientes']:
            st.info("No hay clientes registrados aún.")
        else:
            # Mostrar lista con botones de habilitar/deshabilitar
            for user, info in st.session_state.db['clientes'].items():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                col1.write(f"**Usuario:** {user}")
                col2.write(f"**Vence:** {info['vence']}")
                color = "green" if info['estado'] == "Habilitado" else "red"
                col3.markdown(f":{color}[{info['estado']}]")
                if col4.button("Cambiar Estado", key=user):
                    nuevo_estado = "Deshabilitado" if info['estado'] == "Habilitado" else "Habilitado"
                    st.session_state.db['clientes'][user]['estado'] = nuevo_estado
                    st.rerun()

    with tab2:
        with st.form("registro_nuevo"):
            st.subheader("Crear Credenciales de Cliente")
            n_user = st.text_input("Definir Usuario")
            n_pass = st.text_input("Definir Clave", type="password")
            n_vence = st.date_input("Fecha de Vencimiento", value=datetime.now() + timedelta(days=30))
            if st.form_submit_button("Guardar y Sincronizar"):
                st.session_state.db['clientes'][n_user] = {
                    'pass': make_hashes(n_pass),
                    'vence': n_vence,
                    'estado': 'Habilitado'
                }
                st.success(f"Cliente {n_user} registrado con éxito.")
                st.rerun()

# --- 5. PANEL DEL CLIENTE ---
else:
    info = st.session_state.db['clientes'][st.session_state.user]
    st.title(f"🏢 Sistema Contable - Usuario: {st.session_state.user}")
    st.sidebar.button("🚪 Salida Rápida", on_click=lambda: st.session_state.clear())
    
    # Alerta automática de vencimiento
    dias = (info['vence'] - datetime.now().date()).days
    if 0 <= dias <= 5:
        st.warning(f"⚠️ Su suscripción vence en {dias} días. Contacte al administrador.")

    st.write("---")
    st.subheader("Módulo de Trabajo")
    # Aquí iría el OCR y la Lupa de Historial
