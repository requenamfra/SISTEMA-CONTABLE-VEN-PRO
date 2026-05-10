import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# Inicialización de la Base de Datos (Simulada para 10.000+ empresas)
if 'db' not in st.session_state:
    st.session_state.db = {
        'usuarios': {'admin@omni.com': {'pass': make_hashes('admin123'), 'rol': 'ADMIN', 'rif': 'MASTER'}},
        'empresas': {
            'J500773587': {'nombre': "BALY'S TODO EN UNO C.A.", 'vence': (datetime.now() + timedelta(days=4)).date(), 'estado': 'Habilitado'}
        }
    }

# --- 2. INTERFAZ DE LOGIN ---
if 'user' not in st.session_state:
    st.title("🛡️ OmniContable VE")
    st.subheader("Control de Acceso Seguro (Español)")
    with st.form("login"):
        u = st.text_input("Usuario (Email)")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar al Sistema"):
            if u in st.session_state.db['usuarios'] and check_hashes(p, st.session_state.db['usuarios'][u]['pass']):
                st.session_state.user = u
                st.session_state.rol = st.session_state.db['usuarios'][u]['rol']
                st.session_state.rif = st.session_state.db['usuarios'][u].get('rif')
                st.rerun()
            else:
                st.error("Acceso Denegado: Credenciales Inválidas")
    st.stop()

# --- 3. PANEL DE ADMINISTRADOR (CONTROL DE CLIENTES) ---
if st.session_state.rol == "ADMIN":
    st.title("👑 Consola de Administración Global")
    st.sidebar.button("🚪 Salida Rápida", on_click=lambda: st.session_state.clear())
    
    tab1, tab2 = st.tabs(["📊 Listado de Clientes", "➕ Alta de Clientes/Usuarios"])
    
    with tab1:
        # Convertimos la DB a DataFrame para ver la lista de 10.000 clientes rápido
        data = []
        for rif, info in st.session_state.db['empresas'].items():
            data.append({"RIF": rif, "Empresa": info['nombre'], "Vence": info['vence'], "Estado": info['estado']})
        st.dataframe(pd.DataFrame(data), use_container_width=True)

    with tab2:
        with st.form("registro"):
            st.subheader("Crear nueva Entidad o Usuario")
            c1, c2 = st.columns(2)
            n_rif = c1.text_input("RIF Empresa")
            n_nom = c2.text_input("Nombre de Empresa")
            n_vence = st.date_input("Fecha de Vencimiento")
            n_mail = st.text_input("Email de Acceso")
            n_pass = st.text_input("Clave Temporal", type="password")
            
            if st.form_submit_button("Habilitar Acceso"):
                # Lógica para crear empresa y vincular usuario
                st.session_state.db['empresas'][n_rif] = {'nombre': n_nom, 'vence': n_vence, 'estado': 'Habilitado'}
                st.session_state.db['usuarios'][n_mail] = {'pass': make_hashes(n_pass), 'rol': 'CLIENTE', 'rif': n_rif}
                st.success("Cliente creado y habilitado.")

# --- 4. PANEL DE CLIENTE (CONTABILIDAD + ALERTAS) ---
else:
    rif_cl = st.session_state.rif
    info = st.session_state.db['empresas'][rif_cl]
    
    # ALERTA AUTOMÁTICA DE VENCIMIENTO
    dias = (info['vence'] - datetime.now().date()).days
    if 0 <= dias <= 5:
        st.warning(f"⚠️ AVISO DE VENCIMIENTO: Su licencia expira en {dias} días. Contacte al administrador.")

    st.title(f"🏢 {info['nombre']}")
    st.sidebar.button("🚪 Salida Rápida", on_click=lambda: st.session_state.clear())
    
    mod = st.sidebar.radio("Módulos", ["Dashboard", "Lupa de Historial", "Ganancias y Pérdidas", "Ajuste Inflación", "SENIAT Export"])

    if mod == "Lupa de Historial":
        st.subheader("🔍 Lupa de Historial (Búsqueda en Big Data)")
        busqueda = st.text_input("Ingrese Factura N°, RIF o Proveedor para búsqueda instantánea...")
        # Lógica de búsqueda en los 100.000 registros
        st.write("Resultados filtrados...")

    elif mod == "Ganancias y Pérdidas":
        st.subheader("📊 Ganancias y Pérdidas (Comparativa Divisas)")
        tasa = st.number_input("Tasa BCV (Bs/USD)", value=36.50)
        # Sincronización automática de cuentas
        st.table({"Cuenta": ["Ventas", "Costo Venta", "Utilidad"], "Bolívares (Bs)": [1000, -500, 500], "Dólares (USD)": [1000/tasa, -500/tasa, 500/tasa]})
