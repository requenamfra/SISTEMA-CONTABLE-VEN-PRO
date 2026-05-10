import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA Y SEGURIDAD ---
st.set_page_config(page_title="OmniContable VE", layout="wide")

# Ocultar menús de navegación de Streamlit y GitHub/Share
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

# --- 2. MEMORIA DEL SISTEMA (PERSISTENCIA DE DATOS) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'usuarios': {'admin@omni.com': {'pass': make_hashes('admin123'), 'rol': 'ADMIN', 'rif': 'MASTER'}},
        'empresas': {
            'J500773587': {
                'nombre': "BALY'S TODO EN UNO C.A.", 
                'vence': (datetime.now() + timedelta(days=30)).date(), 
                'estado': 'Habilitado'
            }
        }
    }

# --- 3. INTERFAZ DE LOGIN ---
if 'auth' not in st.session_state:
    st.title("🛡️ OmniContable VE: Control de Acceso")
    with st.form("login_form"):
        u = st.text_input("Usuario (Email)")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar al Sistema"):
            if u in st.session_state.db['usuarios'] and check_hashes(p, st.session_state.db['usuarios'][u]['pass']):
                st.session_state.auth = True
                st.session_state.user = u
                st.session_state.rol = st.session_state.db['usuarios'][u]['rol']
                st.session_state.rif = st.session_state.db['usuarios'][u].get('rif')
                st.rerun()
            else:
                st.error("Credenciales Inválidas")
    st.stop()

# --- 4. PANEL DE ADMINISTRADOR ---
if st.session_state.rol == "ADMIN":
    st.title("👑 Consola de Administración Global")
    st.sidebar.button("🚪 Salida Rápida", on_click=lambda: st.session_state.clear())
    
    tab1, tab2, tab3 = st.tabs(["📊 Listado de Clientes", "🏢 Alta de Empresas", "👤 Usuarios Adicionales"])
    
    with tab1:
        st.subheader("Control Maestro y Estado de Pagos")
        if not st.session_state.db['empresas']:
            st.info("No hay empresas registradas.")
        else:
            # Encabezado de tabla
            col_h = st.columns([2, 3, 2, 2, 2])
            col_h[0].write("**RIF**")
            col_h[1].write("**Empresa**")
            col_h[2].write("**Vence**")
            col_h[3].write("**Estado**")
            col_h[4].write("**Acción**")
            st.divider()

            for rif, info in st.session_state.db['empresas'].items():
                c = st.columns([2, 3, 2, 2, 2])
                c[0].write(rif)
                c[1].write(info['nombre'])
                c[2].write(str(info['vence']))
                
                # Semáforo de Estado
                status_color = "green" if info['estado'] == "Habilitado" else "red"
                c[3].markdown(f":{status_color}[{info['estado']}]")
                
                # Botón de Habilitar/Deshabilitar
                btn_label = "🚫 Suspender" if info['estado'] == "Habilitado" else "✅ Activar"
                if c[4].button(btn_label, key=f"btn_{rif}"):
                    nuevo = "Deshabilitado" if info['estado'] == "Habilitado" else "Habilitado"
                    st.session_state.db['empresas'][rif]['estado'] = nuevo
                    st.rerun()

    with tab2:
        st.subheader("Registrar Nueva Entidad (Empresa)")
        with st.form("new_entidad"):
            n_rif = st.text_input("RIF Empresa")
            n_nom = st.text_input("Razón Social")
            n_vence = st.date_input("Fecha de Vencimiento", value=datetime.now() + timedelta(days=30))
            n_mail = st.text_input("Email de Acceso (Administrador Cliente)")
            n_pass = st.text_input("Clave Inicial", type="password")
            
            if st.form_submit_button("Crear y Habilitar Empresa"):
                if n_rif and n_nom and n_mail:
                    st.session_state.db['empresas'][n_rif] = {'nombre': n_nom, 'vence': n_vence.date() if hasattr(n_vence, 'date') else n_vence, 'estado': 'Habilitado'}
                    st.session_state.db['usuarios'][n_mail] = {'pass': make_hashes(n_pass), 'rol': 'CLIENTE', 'rif': n_rif}
                    st.success(f"Empresa {n_nom} registrada correctamente.")
                    st.rerun()

    with tab3:
        st.subheader("Usuarios Adicionales (Multiusuario por Empresa)")
        with st.form("extra_user"):
            emp_target = st.selectbox("Seleccione Empresa", list(st.session_state.db['empresas'].keys()))
            u_mail = st.text_input("Email del Colaborador")
            u_pass = st.text_input("Clave", type="password")
            if st.form_submit_button("Vincular Usuario"):
                st.session_state.db['usuarios'][u_mail] = {'pass': make_hashes(u_pass), 'rol': 'CLIENTE', 'rif': emp_target}
                st.success("Usuario vinculado con éxito.")

# --- 5. PANEL DE CLIENTE (VISTA OPERATIVA) ---
else:
    rif_cl = st.session_state.rif
    info = st.session_state.db['empresas'].get(rif_cl)
    
    if info['estado'] == "Deshabilitado":
        st.error("🚫 ACCESO SUSPENDIDO: Por favor, contacte al administrador para habilitar su suscripción.")
        st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.clear())
        st.stop()

    st.title(f"🏢 {info['nombre']}")
    st.sidebar.button("🚪 Salida Rápida", on_click=lambda: st.session_state.clear())
    
    # Alerta de Vencimiento (5 días antes)
    dias = (info['vence'] - datetime.now().date()).days
    if 0 <= dias <= 5:
        st.warning(f"⚠️ AVISO: Su licencia vence en {dias} días. Contacte soporte.")

    menu = st.sidebar.radio("Módulos", ["🔍 Lupa de Historial", "📊 Ganancias y Pérdidas", "🏛️ Fiscal SENIAT", "⚖️ Balance General"])

    if menu == "🔍 Lupa de Historial":
        st.subheader("🔍 Lupa de Historial: Búsqueda en Big Data")
        busqueda = st.text_input("Ingrese Factura N°, RIF de Proveedor o Fecha...")
        # Simulación de Big Data (100,000 registros)
        st.write("Resultados filtrados en 0.02s...")

    elif menu == "📊 Ganancias y Pérdidas":
        st.subheader("Estado de Resultados (Comparativa USD)")
        tasa = st.number_input("Tasa BCV (Bs/USD)", value=36.50)
        st.table({
            "Cuenta": ["Ventas Netas", "Costo de Ventas", "Utilidad Bruta", "Gastos Operativos", "Resultado Ejercicio"],
            "Monto (Bs)": [500000.0, -200000.0, 300000.0, -100000.0, 200000.0],
            "Equiv. (USD)": [500000/tasa, -200000/tasa, 300000/tasa, -100000/tasa, 200000/tasa]
        })
