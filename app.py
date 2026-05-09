import streamlit as st
import pandas as pd
from datetime import datetime

# 1. BLOQUEO DE INTERFAZ Y ESTÉTICA PROFESIONAL
st.set_page_config(page_title="VEN-PRO v70.0 GLOBAL", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, label, .stMarkdown { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button {
        width: 100% !important; border: 2px solid #000 !important; 
        background-color: #e8e8e8 !important; color: black !important; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS INICIAL (EN CERO PARA LA VENTA)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'rol' not in st.session_state: st.session_state.rol = None
if 'empresas' not in st.session_state: st.session_state.empresas = {}
if 'usuarios_pago' not in st.session_state: 
    # Lista de control de pagos (El Admin los activa/bloquea aquí)
    st.session_state.usuarios_pago = {"ADMIN": "ACTIVO"}

# 3. PANTALLA DE ACCESO BLINDADA
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login"):
            st.subheader("🔐 Credenciales de Acceso")
            u_input = st.text_input("USUARIO / RIF:").upper()
            p_input = st.text_input("CONTRASEÑA:", type="password")
            entrar = st.form_submit_button("🔓 ACCEDER")
            
            if entrar:
                if u_input == "ADMIN" and p_input == "VEN2026":
                    st.session_state.auth, st.session_state.rol = True, "ADMIN"
                    st.rerun()
                elif u_input in st.session_state.usuarios_pago and st.session_state.usuarios_pago[u_input] == "ACTIVO":
                    # Aquí iría la validación de contraseña de cada usuario
                    st.session_state.auth, st.session_state.rol = True, "USUARIO"
                    st.rerun()
                elif u_input in st.session_state.usuarios_pago and st.session_state.usuarios_pago[u_input] == "BLOQUEADO":
                    st.error("❌ ACCESO BLOQUEADO. Por favor, regularice su pago mensual.")
                else:
                    st.error("❌ Usuario no registrado o pago pendiente.")
    st.stop()

# 4. BARRA LATERAL (CONTROL TOTAL)
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Consultar Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    h_anio = st.selectbox("Consultar Año:", [2024, 2025, 2026], index=2)
    st.write("---")
    
    opciones = ["📊 DASHBOARD", "🏢 GESTIÓN DE 100 EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 XML / TXT"]
    if st.session_state.rol == "ADMIN": opciones.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("MÓDULOS:", opciones)
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 5. DESARROLLO DE MÓDULOS FULL DATA
st.title(f"{menu} - {h_mes} {h_anio}")

# --- PANEL ADMINISTRADOR (CONTROL DE PAGOS) ---
if menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Control de Suscripciones Mensuales")
    with st.expander("➕ REGISTRAR NUEVO CLIENTE (SUSCRIPCIÓN)"):
        n_user = st.text_input("Usuario/RIF del nuevo cliente:").upper()
        if st.button("Activar Cliente"):
            st.session_state.usuarios_pago[n_user] = "ACTIVO"
            st.success(f"Cliente {n_user} activado.")
    
    st.write("### Estado de Cobranza")
    for user, status in st.session_state.usuarios_pago.items():
        if user == "ADMIN": continue
        c1, c2, c3 = st.columns([2, 2, 1])
        c1.write(f"**Usuario:** {user}")
        nuevo_st = c2.selectbox(f"Acción {user}", ["ACTIVO", "BLOQUEADO"], index=0 if status=="ACTIVO" else 1, key=user)
        st.session_state.usuarios_pago[user] = nuevo_st
        if nuevo_st == "BLOQUEADO": c3.warning("🚫 Sin Acceso")
        else: c3.success("✅ Con Acceso")

# --- GESTIÓN DE 100 EMPRESAS ---
elif menu == "🏢 GESTIÓN DE 100 EMPRESAS":
    st.subheader("Cartera de Clientes (Capacidad: 100 Empresas)")
    with st.expander("➕ REGISTRAR EMPRESA A CONTABILIZAR"):
        c1, c2 = st.columns(2)
        n_e = c1.text_input("Nombre de la Empresa:")
        r_e = c2.text_input("RIF:")
        if st.button("Guardar en Cartera"):
            if len(st.session_state.empresas) < 100:
                st.session_state.empresas[r_e] = {"Nombre": n_e, "RIF": r_e, "Fecha_Reg": datetime.now()}
                st.success("Empresa añadida.")
            else: st.error("Capacidad máxima de 100 empresas alcanzada.")
    
    st.table(pd.DataFrame.from_dict(st.session_state.empresas, orient='index'))

# --- LIBROS SEPARADOS ---
elif menu == "🛒 LIBRO DE COMPRAS":
    st.file_uploader("📥 CARGAR COMPRAS (PDF, EXCEL, FOTO)", key="comp", accept_multiple_files=True)
    st.info("Buscando en historial...")
    st.table(pd.DataFrame({"Fecha": [], "RIF Proveedor": [], "Base": [], "IVA": [], "Total": []}))

elif menu == "💰 LIBRO DE VENTAS":
    st.file_uploader("📥 CARGAR VENTAS (PDF, EXCEL, FOTO)", key="vent", accept_multiple_files=True)
    st.table(pd.DataFrame({"Fecha": [], "Cliente": [], "Base": [], "IVA": [], "Total": []}))

elif menu == "📖 DIARIO Y MAYOR":
    st.subheader("Libros Integrados")
    st.file_uploader("📥 CARGAR SOPORTES (PDF, EXCEL, FOTO)", key="cont")
    st.write("### Asientos Contables")
    st.table(pd.DataFrame({"Asiento": ["001"], "Cuenta": ["Banco"], "Debe": ["0.00"], "Haber": ["0.00"]}))

# --- ALCALDÍA ---
elif menu == "🏛️ ALCALDÍA":
    st.markdown("""
    **Control de Tributos Municipales:**
    - **IAE/ISAE:** Impuesto sobre Actividades Económicas (Ingresos Brutos).
    - **Inmuebles Urbanos (Derecho de Frente):** Propiedad inmobiliaria.
    - **Vehículos:** Tasa anual por propiedad mecánica.
    - **Propaganda y Publicidad:** Vallas, letreros y publicidad en vehículos.
    - **Espectáculos Públicos:** Tasas sobre eventos y azar.
    - **Tasas Administrativas:** ASEO, trámites y registros.
    """)
    st.selectbox("Seleccione Tributo para Control:", ["IAE", "Derecho de Frente", "Vehículos", "Publicidad", "Espectáculos", "ASEO"])
    st.file_uploader("📥 SUBIR PAGOS / COMPROBANTES")

# --- PARAFISCALES ---
elif menu == "🏢 PARAFISCALES":
    st.markdown("""
    **Control Parafiscal:**
    - **IVSS:** Seguro Social Obligatorio.
    - **FAOV:** Vivienda (BANAVIH).
    - **INCES:** Capacitación técnica.
    - **Régimen de Empleo:** Paro Forzoso.
    - **Nueva Ley de Pensiones (2025):** Protección social gestionada por SENIAT.
    """)
    st.selectbox("Seleccione Ente:", ["IVSS", "FAOV", "INCES", "Empleo", "Pensiones 2025"])
    st.file_uploader("📥 SUBIR PLANILLAS / PAGOS")

# --- XML / TXT ---
elif menu == "📤 XML / TXT":
    st.subheader("Generación y Control de Archivos Fiscales")
    st.file_uploader("📥 CARGAR PAGOS SENIAT (PDF/TXT/XML)")
    c1, c2 = st.columns(2)
    with c1: st.button("📦 GENERAR XML IVA")
    with c2: st.button("📄 GENERAR TXT ISLR")
