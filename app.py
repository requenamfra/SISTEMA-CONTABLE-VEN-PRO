import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. BLOQUEO DE INTERFAZ Y CONFIGURACIÓN VISUAL
st.set_page_config(page_title="VEN-PRO v80 - SISTEMA CONTABLE GLOBAL", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, label, th, td { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button {
        width: 100% !important; border: 2px solid #000 !important; 
        background-color: #e8e8e8 !important; color: black !important; font-weight: bold;
    }
    .status-rojo { color: #FF0000 !important; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS MAESTRA (VACÍA PARA VENTA)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = {}
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = {}

# 3. PANTALLA DE ACCESO (LOGIN)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO v80</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login"):
            st.subheader("🔐 Acceso Administrador / Suscriptor")
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            if st.form_submit_button("🔓 ENTRAR AL SISTEMA"):
                if u == "ADMIN" and p == "VEN2026":
                    st.session_state.auth, st.session_state.rol, st.session_state.user = True, "ADMIN", u
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]["clave"] == p:
                    if st.session_state.db_clientes[u]["estatus"] == "Activo":
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("❌ SUSCRIPCIÓN VENCIDA.")
                else: st.error("❌ Datos incorrectos.")
    st.stop()

# 4. BARRA LATERAL (LUPA DE HISTORIAL Y MODULOS)
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    if st.session_state.rol == "CLIENTE":
        venc = datetime.strptime(st.session_state.db_clientes[st.session_state.user]["vencimiento"], "%Y-%m-%d")
        dias_rest = (venc.date() - date.today()).days
        if dias_rest <= 5:
            st.markdown(f"<p class='status-rojo'>⚠️ ADVERTENCIA: {dias_rest} DÍAS PARA VENCER</p>", unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    st.write("---")
    
    modulos = ["📊 DASHBOARD", "🏢 GESTIÓN +100 EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 LIBRO DIARIO", "📚 LIBRO MAYOR", "🏛️ ALCALDÍA GIRARDOT", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": modulos.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("SECCIONES:", modulos)
    if st.button("🔴 SALIR"):
        st.session_state.auth = False
        st.rerun()

# 5. FUNCIONALIDAD DE VACIADO INTELIGENTE (Bolívares Bs.)
def leer_factura(archivo):
    # Simulación de extracción de datos de imagen/PDF para vaciado automático
    return {
        "Nombre / Razón Social": "VENDEDOR EJEMPLO C.A", "Factura N°": "000123", "Nº Control": "00-456",
        "Total": 1160.00, "Exento": 0.00, "Base": 1000.00, "IVA": 160.00
    }

# 6. DESARROLLO DE MÓDULOS FULL DATA
st.title(f"{menu} - {h_mes} {h_anio}")

if menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Lista de Clientes Suscriptores")
    with st.expander("➕ REGISTRAR NUEVO CLIENTE (SUSCRIPTOR)"):
        c1, c2, c3 = st.columns(3)
        n_u = c1.text_input("RIF Cliente:")
        n_p = c2.text_input("Clave:")
        n_f = c3.date_input("Vencimiento:")
        if st.button("Habilitar"):
            st.session_state.db_clientes[n_u] = {"clave": n_p, "estatus": "Activo", "vencimiento": str(n_f)}
            st.rerun()
    
    if st.session_state.db_clientes:
        df_adm = pd.DataFrame.from_dict(st.session_state.db_clientes, orient='index').reset_index()
        st.write("### Suscriptores Activos")
        st.dataframe(df_adm)
        bloq = st.selectbox("Bloquear/Activar Usuario:", df_adm['index'])
        if st.button("Cambiar Estatus"):
            st.session_state.db_clientes[bloq]["estatus"] = "Inactivo" if st.session_state.db_clientes[bloq]["estatus"] == "Activo" else "Activo"
            st.rerun()

elif menu == "🏢 GESTIÓN +100 EMPRESAS":
    st.subheader("Registro de Carteras Contables")
    with st.form("emp"):
        n_e = st.text_input("Nombre / Razón Social Empresa:")
        r_e = st.text_input("R.I.F. Empresa:")
        if st.form_submit_button("Guardar Empresa"):
            st.session_state.db_empresas[r_e] = {"Nombre": n_e, "Fecha": str(date.today())}
    st.write(f"Capacidad: {len(st.session_state.db_empresas)} / 100")
    st.table(pd.DataFrame.from_dict(st.session_state.db_empresas, orient='index'))

elif menu == "🛒 LIBRO DE COMPRAS":
    st.subheader("Carga y Vaciado de Compras")
    up = st.file_uploader("📥 SUBIR FACTURA (PDF/FOTO)", type=['pdf', 'png', 'jpg'])
    if up:
        data = leer_factura(up)
        st.success("✅ Factura leída. Verifique los montos abajo en la tabla de registro.")
    
    st.write("### Registro de Compras (Carga Manual y Automática)")
    df_com = pd.DataFrame(columns=["Nombre / Razón Social Proveedor", "DESCRIPCIÓN Y BANCO", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"])
    st.data_editor(df_com, num_rows="dynamic", use_container_width=True)

elif menu == "💰 LIBRO DE VENTAS":
    st.subheader("Carga y Vaciado de Ventas")
    up = st.file_uploader("📥 SUBIR FACTURA DE VENTA", key="v")
    st.write("### Registro de Ventas")
    df_ven = pd.DataFrame(columns=["Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"])
    st.data_editor(df_ven, num_rows="dynamic", use_container_width=True)

elif menu == "📖 LIBRO DIARIO":
    st.subheader("Catálogo de Cuentas VEN-NIIF")
    with st.expander("Ver Naturaleza de Cuentas"):
        st.write("**Deudoras:** Activos, Gastos, Costos. **Acreedoras:** Pasivos, Patrimonio, Ingresos.")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Cuenta", "Descripción del Asiento", "Debe (Bs.)", "Haber (Bs.)"]), num_rows="dynamic", use_container_width=True)

elif menu == "📚 LIBRO MAYOR":
    st.subheader("Auxiliar de Cuentas")
    cta = st.selectbox("Seleccione Cuenta:", ["Caja Chica", "Bancos", "IVA Crédito", "Ventas", "Cuentas por Pagar"])
    st.table(pd.DataFrame(columns=["Fecha", "Explicación", "Debe", "Haber", "Saldo"]))

elif menu == "🏢 PARAFISCALES":
    inst = st.selectbox("Institución:", ["IVSS", "FAOV (BANAVIH)", "INCES", "Régimen Empleo", "Nueva Ley de Pensiones (2025)"])
    st.file_uploader(f"Cargar Comprobante de {inst}")
    st.data_editor(pd.DataFrame(columns=["Mes", "Institución", "Monto Pagado", "Referencia"]), num_rows="dynamic")

elif menu == "🏛️ ALCALDÍA GIRARDOT":
    st.info("Municipio Girardot, Maracay - Aragua")
    trib = st.selectbox("Tributo:", ["IAE/ISAE", "Inmuebles Urbanos", "Vehículos", "Publicidad", "ASEO (Sateca)"])
    st.file_uploader(f"Cargar Pago de {trib}")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Tributo", "Monto Bs.", "Estatus"]), num_rows="dynamic")

elif menu == "📊 DASHBOARD":
    st.subheader("Resumen General Contable")
    c1, c2, c3 = st.columns(3)
    c1.metric("VENTAS TOTALES", "0,00 Bs.")
    c2.metric("COMPRAS TOTALES", "0,00 Bs.")
    c3.metric("IVA POR PAGAR", "0,00 Bs.")
    st.write("---")
    st.write("### Estado de Solvencias Municipales y Parafiscales")
    st.info("No hay deudas pendientes en este periodo.")
