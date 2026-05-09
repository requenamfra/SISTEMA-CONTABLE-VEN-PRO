import streamlit as st
import pandas as pd
from datetime import datetime

# 1. SEGURIDAD Y BLOQUEO DE INTERFAZ EXTERNA
st.set_page_config(page_title="VEN-PRO v65.0 - SISTEMA CONTABLE", layout="wide")
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
    .status-vencido { color: #FF0000 !important; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS INICIAL (TODO EN CERO PARA VENTA)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state:
    st.session_state.db_clientes = {
        "CLIENTE_DEMO": {"clave": "12345", "estatus": "Activo", "vencimiento": "2026-05-30"}
    }
if 'db_empresas' not in st.session_state:
    st.session_state.db_empresas = {} # Capacidad para 100+ empresas

# 3. PANTALLA DE ACCESO (LOGIN)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO PRO</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login"):
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            if st.form_submit_button("🔓 ENTRAR"):
                if u == "ADMIN" and p == "VEN2026":
                    st.session_state.auth, st.session_state.rol, st.session_state.user = True, "ADMIN", u
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]["clave"] == p:
                    if st.session_state.db_clientes[u]["estatus"] == "Activo":
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("❌ SUSCRIPCIÓN VENCIDA. Contacte al administrador.")
                else: st.error("❌ Datos incorrectos.")
    st.stop()

# 4. BARRA LATERAL (LUPA DE HISTORIAL Y MENÚ)
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    # ADVERTENCIA DE PAGO
    if st.session_state.rol == "CLIENTE":
        st.markdown(f"<p class='status-vencido'>⚠️ SU MES VENCE: {st.session_state.db_clientes[st.session_state.user]['vencimiento']}</p>", unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    st.write("---")
    
    modulos = ["📊 DASHBOARD", "🏢 REGISTRO DE EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA GIRARDOT", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": modulos.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("SECCIONES:", modulos)
    if st.button("🔴 SALIR"):
        st.session_state.auth = False
        st.rerun()

# 5. DESARROLLO DE MÓDULOS FULL DATA
st.title(f"{menu} - {h_mes} {h_anio}")

# --- PANEL ADMINISTRADOR (SOLO TÚ) ---
if menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Control de Suscripciones y Clientes")
    with st.expander("➕ REGISTRAR NUEVO CLIENTE (SUSCRIPTOR)"):
        nc = st.text_input("Usuario/RIF Cliente:")
        pc = st.text_input("Clave Cliente:")
        fv = st.date_input("Fecha de Vencimiento:")
        if st.button("Crear Suscripción"):
            st.session_state.db_clientes[nc] = {"clave": pc, "estatus": "Activo", "vencimiento": str(fv)}
            st.success("Cliente habilitado.")
    
    st.write("### Lista de Clientes Activos / Inactivos")
    for c, data in st.session_state.db_clientes.items():
        c1, c2, c3 = st.columns([2, 2, 1])
        c1.write(f"👤 {c}")
        nuevo_est = c2.selectbox(f"Estado {c}", ["Activo", "Inactivo"], index=0 if data["estatus"]=="Activo" else 1)
        st.session_state.db_clientes[c]["estatus"] = nuevo_est
        c3.write(f"📅 {data['vencimiento']}")

# --- REGISTRO DE EMPRESAS (+100 CAPACIDAD) ---
elif menu == "🏢 REGISTRO DE EMPRESAS (0/100)":
    st.subheader("Cartera de Empresas del Usuario")
    with st.form("new_emp"):
        n_e = st.text_input("Nombre de la Empresa:")
        r_e = st.text_input("RIF:")
        if st.form_submit_button("💾 Guardar Empresa"):
            st.session_state.db_empresas[r_e] = {"Nombre": n_e, "Libros": "Vacíos"}
            st.success(f"Empresa {n_e} guardada en el sistema.")
    st.write("### Empresas Registradas:")
    st.table(pd.DataFrame.from_dict(st.session_state.db_empresas, orient='index'))

# --- LIBROS SEPARADOS ---
elif menu == "🛒 LIBRO DE COMPRAS":
    st.subheader("Lupa de Historial: Compras Registradas")
    st.file_uploader("📥 Cargar Facturas (PDF/Excel/Foto)", type=['pdf', 'xlsx', 'png', 'jpg'], key="c")
    st.info("Información actual: 0 registros (Listo para vaciar data).")

elif menu == "💰 LIBRO DE VENTAS":
    st.subheader("Lupa de Historial: Ventas Registradas")
    st.file_uploader("📥 Cargar Facturas (PDF/Excel/Foto)", type=['pdf', 'xlsx', 'png', 'jpg'], key="v")

elif menu == "📖 DIARIO Y MAYOR":
    st.subheader("Contabilidad General: Libros Diario y Mayor")
    st.text_input("🔍 Lupa: Buscar asiento por cuenta o monto:")
    st.table(pd.DataFrame(columns=["Fecha", "Cuenta", "Debe", "Haber"]))
    st.file_uploader("📥 Cargar Movimientos Bancarios/Asientos", key="dm")

# --- ALCALDÍA (FULL INFO) ---
elif menu == "🏛️ ALCALDÍA GIRARDOT":
    st.markdown("""
    **Seleccione Tributo para Control de Pagos:**
    * **IAE/ISAE:** Actividades Económicas (Ingresos Brutos).
    * **Derecho de Frente:** Inmuebles Urbanos.
    * **Vehículos:** Tasa anual.
    * **Publicidad:** Propaganda Comercial.
    * **ASEO (Sateca):** Tasas de servicio.
    """)
    st.selectbox("Tributo:", ["IAE", "Derecho de Frente", "Vehículos", "Publicidad", "Espectáculos", "ASEO"])
    st.file_uploader("📥 Cargar Comprobante de Pago")

# --- PARAFISCALES (FULL INFO) ---
elif menu == "🏢 PARAFISCALES":
    st.markdown("""
    **Control Parafiscal Obligatorio:**
    * **IVSS:** Seguro Social.
    * **FAOV:** Vivienda (BANAVIH).
    * **INCES:** Capacitación Técnica.
    * **Empleo:** Régimen Prestacional.
    * **Pensiones (2025):** Nuevo aporte SENIAT.
    """)
    st.selectbox("Institución:", ["IVSS", "FAOV", "INCES", "Régimen Empleo", "Ley Pensiones"])
    st.file_uploader("📥 Cargar Planilla de Pago / Solvencia")

# --- XML/TXT ---
elif menu == "📤 SENIAT (XML/TXT)":
    st.subheader("Control de Retenciones y Archivos Fiscales")
    st.file_uploader("📥 Cargar TXT/XML para auditoría y control de pagos")
    c1, c2 = st.columns(2)
    c1.button("📦 Generar XML (IVA)")
    c2.button("📄 Generar TXT (ISLR)")
