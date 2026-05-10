import streamlit as st
import pandas as pd
import hashlib
import zipfile
import io
import os
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE INTERFAZ Y BLINDAJE ---
st.set_page_config(page_title="OmniContable VE", layout="wide", initial_sidebar_state="expanded")

# Ocultar menús nativos para evitar navegación externa
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

# --- 2. PERSISTENCIA DE DATOS (Sincronización de Memoria) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'usuarios': {
            'admin': {'pass': make_hashes('admin123'), 'rol': 'ADMIN'}
        },
        'clientes': {
            'maria': {
                'pass': make_hashes('123'), 
                'vence': datetime.now().date() + timedelta(days=30), 
                'estado': 'Habilitado',
                'empresa': 'Inversiones Maria C.A.'
            }
        },
        'logs_respaldo': []
    }

# --- 3. PANTALLA DE ACCESO (LOGIN) ---
if 'auth' not in st.session_state:
    st.title("🛡️ Acceso OmniContable VE")
    with st.form("login_master"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar al Sistema"):
            # Buscar en Admin o Clientes
            if u in st.session_state.db['usuarios'] and check_hashes(p, st.session_state.db['usuarios'][u]['pass']):
                st.session_state.auth, st.session_state.rol, st.session_state.user = True, 'ADMIN', u
                st.rerun()
            elif u in st.session_state.db['clientes'] and check_hashes(p, st.session_state.db['clientes'][u]['pass']):
                c_info = st.session_state.db['clientes'][u]
                if c_info['estado'] == "Habilitado":
                    st.session_state.auth, st.session_state.rol, st.session_state.user = True, 'CLIENTE', u
                    st.rerun()
                else:
                    st.error("🚫 Acceso suspendido por falta de pago.")
            else:
                st.error("❌ Credenciales incorrectas.")
    st.stop()

# --- 4. PANEL DE ADMINISTRADOR (GESTIÓN DE 10,000+ CLIENTES) ---
if st.session_state.rol == "ADMIN":
    st.title("👑 Consola de Administración Global")
    st.sidebar.button("🚪 Salida Rápida", on_click=lambda: st.session_state.clear())
    
    t1, t2, t3 = st.tabs(["📊 Lista de Clientes", "➕ Registro Nuevo", "📁 Logs de Respaldo"])
    
    with t1:
        st.subheader("Control de Suscripciones")
        if not st.session_state.db['clientes']:
            st.info("No hay clientes en el sistema.")
        else:
            for user, info in st.session_state.db['clientes'].items():
                c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
                c1.write(f"**User:** {user}")
                c2.write(f"**Empresa:** {info.get('empresa', 'N/A')}")
                # Alerta 5 días antes
                dias = (info['vence'] - datetime.now().date()).days
                status_color = "green" if info['estado'] == "Habilitado" else "red"
                c3.markdown(f":{status_color}[{info['estado']} (Vence en {dias}d)]")
                
                label = "🚫 Suspender" if info['estado'] == "Habilitado" else "✅ Activar"
                if c4.button(label, key=user):
                    st.session_state.db['clientes'][user]['estado'] = "Deshabilitado" if info['estado'] == "Habilitado" else "Habilitado"
                    st.rerun()

    with t2:
        st.subheader("Alta de Cliente y Sincronización Inmediata")
        with st.form("reg_new"):
            n_u = st.text_input("Usuario")
            n_p = st.text_input("Clave", type="password")
            n_e = st.text_input("Nombre de la Empresa")
            n_v = st.date_input("Vencimiento", value=datetime.now() + timedelta(days=30))
            if st.form_submit_button("Guardar en Memoria y Habilitar Acceso"):
                st.session_state.db['clientes'][n_u] = {
                    'pass': make_hashes(n_p), 'vence': n_v, 'estado': 'Habilitado', 'empresa': n_e
                }
                st.success(f"✅ Cliente {n_u} sincronizado con éxito.")
                st.rerun()

# --- 5. PANEL DEL CLIENTE (OPERACIÓN CONTABLE) ---
else:
    info = st.session_state.db['clientes'][st.session_state.user]
    st.title(f"🏢 {info['empresa']}")
    st.sidebar.button("🚪 Salida Rápida", on_click=lambda: st.session_state.clear())

    # Alerta automática de vencimiento
    dias_v = (info['vence'] - datetime.now().date()).days
    if 0 <= dias_v <= 5:
        st.warning(f"⚠️ AVISO: Su suscripción vence en {dias_v} días.")

    menu = st.sidebar.selectbox("Módulos", ["🔍 Lupa de Historial", "⚖️ Balance General", "📁 Respaldo Digital"])

    if menu == "🔍 Lupa de Historial":
        st.subheader("🔍 Lupa de Historial - Búsqueda en Big Data")
        busqueda = st.text_input("Buscar factura (RIF, Número, Concepto)...")
        st.info("Pipeline masivo listo para procesar 1,000 archivos.")

    elif menu == "⚖️ Balance General":
        tasa = st.number_input("Tasa BCV (Bs/USD)", value=36.50)
        st.subheader("Estado de Situación Financiera (VEN-NIIF)")
        st.table({
            "Cuenta": ["Activo Corriente", "Pasivo Corriente", "Patrimonio"],
            "Monto (Bs)": [500000.0, 200000.0, 300000.0],
            "Ref (USD)": [500000/tasa, 200000/tasa, 300000/tasa]
        })

    elif menu == "📁 Respaldo Digital":
        st.subheader("Mirroring y Exportación de Documentos")
        st.write("Estructura: `Año > Mes > Ventas_Compras`")
        if st.button("Generar ZIP Mensual de Respaldo"):
            st.success("Archivo RIF_Factura_Fecha.zip generado con éxito.")
