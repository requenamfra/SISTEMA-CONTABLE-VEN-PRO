import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA Y SEGURIDAD VISUAL ---
st.set_page_config(page_title="OmniContable VE", layout="wide")

# Ocultar menús externos de Streamlit (Botones de arriba y footer)
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

# --- 2. MEMORIA DEL SISTEMA (BASE DE DATOS INTEGRADA) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'usuarios': {'admin@omni.com': {'pass': make_hashes('admin123'), 'rol': 'ADMIN', 'rif': 'MASTER'}},
        'empresas': {}
    }

# --- 3. INTERFAZ DE LOGIN ---
if 'auth' not in st.session_state:
    st.title("🛡️ OmniContable VE - Acceso Profesional")
    with st.form("login_form"):
        u = st.text_input("Correo Electrónico")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            if u in st.session_state.db['usuarios'] and check_hashes(p, st.session_state.db['usuarios'][u]['pass']):
                st.session_state.auth = True
                st.session_state.user = u
                st.session_state.rol = st.session_state.db['usuarios'][u]['rol']
                st.session_state.rif = st.session_state.db['usuarios'][u].get('rif')
                st.rerun()
            else:
                st.error("Credenciales incorrectas o usuario inexistente.")
    st.stop()

# --- 4. PANEL DE ADMINISTRADOR (CONTROL MAESTRO) ---
if st.session_state.rol == "ADMIN":
    st.title("👑 Consola de Administración Global")
    st.sidebar.button("🚪 Salida Rápida", on_click=lambda: st.session_state.clear())
    
    tab1, tab2, tab3 = st.tabs(["📊 Listado de Clientes", "🏢 Alta de Empresas", "👤 Usuarios Adicionales"])
    
    with tab1:
        st.subheader("Control de Suscripciones y Pagos")
        if not st.session_state.db['empresas']:
            st.info("No hay registros. Comience en la pestaña 'Alta de Empresas'.")
        else:
            # Lista dinámica para 10,000+ clientes
            df_data = []
            for rif, info in st.session_state.db['empresas'].items():
                df_data.append({
                    "RIF": rif,
                    "Empresa": info['nombre'],
                    "Vencimiento": info['vence'],
                    "Estado": info['estado']
                })
            
            # Tabla interactiva con botones de acción
            for rif, info in st.session_state.db['empresas'].items():
                col1, col2, col3, col4 = st.columns([2, 4, 2, 2])
                col1.write(f"**{rif}**")
                col2.write(info['nombre'])
                
                # Alerta visual de vencimiento
                dias_rest = (info['vence'] - datetime.now().date()).days
                color = "red" if info['estado'] == "Deshabilitado" or dias_rest < 0 else "green"
                col3.markdown(f":{color}[{info['estado']} ({dias_rest} días)]")
                
                # Botón de Habiltar/Deshabilitar
                label = "🚫 Suspender" if info['estado'] == "Habilitado" else "✅ Activar"
                if col4.button(label, key=f"pago_{rif}"):
                    nuevo = "Deshabilitado" if info['estado'] == "Habilitado" else "Habilitado"
                    st.session_state.db['empresas'][rif]['estado'] = nuevo
                    st.rerun()

    with tab2:
        st.subheader("Registrar Nueva Entidad")
        with st.form("reg_master"):
            e_rif = st.text_input("RIF (Ej: J123456789)")
            e_nom = st.text_input("Razón Social")
            e_vence = st.date_input("Vencimiento de Suscripción")
            st.divider()
            e_mail = st.text_input("Correo del Dueño")
            e_pass = st.text_input("Clave Inicial", type="password")
            
            if st.form_submit_button("Dar de Alta y Sincronizar Login"):
                # Sincronización inmediata con la memoria de ingreso
                st.session_state.db['empresas'][e_rif] = {'nombre': e_nom, 'vence': e_vence, 'estado': 'Habilitado'}
                st.session_state.db['usuarios'][e_mail] = {'pass': make_hashes(e_pass), 'rol': 'CLIENTE', 'rif': e_rif}
                st.success(f"Empresa {e_nom} registrada. El cliente ya puede ingresar.")
                st.rerun()

    with tab3:
        st.subheader("Añadir Usuarios Adicionales (Colaboradores)")
        with st.form("multi_user"):
            target = st.selectbox("Asignar a Empresa", list(st.session_state.db['empresas'].keys()))
            u_mail = st.text_input("Correo del nuevo usuario")
            u_pass = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Vincular Acceso"):
                st.session_state.db['usuarios'][u_mail] = {'pass': make_hashes(u_pass), 'rol': 'CLIENTE', 'rif': target}
                st.success("Acceso compartido habilitado.")

# --- 5. PANEL DE CLIENTE (VISTA OPERATIVA) ---
else:
    info = st.session_state.db['empresas'].get(st.session_state.rif)
    
    # Bloqueo por falta de pago
    if info['estado'] == "Deshabilitado":
        st.error("🚫 ACCESO RESTRINGIDO: Su suscripción ha vencido o está suspendida. Contacte al administrador.")
        st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.clear())
        st.stop()

    st.title(f"🏢 Panel Contable: {info['nombre']}")
    st.sidebar.button("🚪 Salida Rápida", on_click=lambda: st.session_state.clear())
    
    # Alerta automática 5 días antes
    dias = (info['vence'] - datetime.now().date()).days
    if 0 <= dias <= 5:
        st.warning(f"⚠️ AVISO: Su suscripción vence en {dias} días. Evite la suspensión del servicio.")

    menu = st.sidebar.selectbox("Módulos", ["🔍 Lupa de Historial", "📊 Estados Financieros", "🏛️ Fiscal & SENIAT"])

    if menu == "🔍 Lupa de Historial":
        st.subheader("🔍 Lupa de Historial (Búsqueda en Big Data)")
        filtro = st.text_input("Buscar factura por RIF, Número o Concepto...")
        st.info("Mostrando últimos movimientos de 100,000 registros...")
        # Aquí irá el motor OCR y búsqueda masiva

    elif menu == "📊 Estados Financieros":
        tasa = st.number_input("Tasa BCV (Bs/USD)", value=36.50)
        st.subheader("Ganancias y Pérdidas (VEN-NIIF)")
        st.table({
            "Cuenta": ["Ingresos Operativos", "Costos de Ventas", "Gastos Administrativos", "Resultado Neto"],
            "Bs": [100000, -40000, -20000, 40000],
            "USD (Ref)": [100000/tasa, -40000/tasa, -20000/tasa, 40000/tasa]
        })
