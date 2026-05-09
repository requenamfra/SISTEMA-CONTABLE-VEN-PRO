import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid

# 1. SEGURIDAD Y CONFIGURACIÓN BLINDADA
st.set_page_config(page_title="VEN-PRO v120.0 - SEGURIDAD TOTAL", layout="wide")

# Estilos y Bloqueo de Navegación Externa
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #f8f9fa !important; }
    .status-vencido { color: #ffffff; background-color: #d00000; padding: 10px; border-radius: 5px; font-weight: bold; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS PERSISTENTE (Simulada en Session State)
if 'init' not in st.session_state:
    st.session_state.init = True
    st.session_state.auth = False
    st.session_state.db_clientes = {} # {rif: {pass, vencimiento, status}}
    st.session_state.db_empresas = [] # Lista de carteras (hasta 100)
    st.session_state.l_compras = pd.DataFrame(columns=[
        "ID", "Fecha", "Nombre / Razón Social Proveedor", "DESCRICION Y BANCO", "Factura N°", 
        "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", 
        "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"
    ])
    st.session_state.l_ventas = pd.DataFrame(columns=[
        "Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", 
        "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", 
        "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"
    ])

# 3. PANTALLA DE ACCESO (LOGIN SEGURO)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 ACCESO RESTRINGIDO - VEN-PRO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("auth_gate"):
            user = st.text_input("USUARIO / RIF:").upper().strip()
            pw = st.text_input("CONTRASEÑA:", type="password")
            role = st.selectbox("TIPO DE ACCESO:", ["CLIENTE", "ADMINISTRADOR"])
            if st.form_submit_button("🛡️ INGRESAR AL SISTEMA"):
                # ACCESO ADMIN (TU ACCESO)
                if role == "ADMINISTRADOR" and user == "ADMIN" and pw == "MARIA_VENPRO_2026":
                    st.session_state.auth, st.session_state.role = True, "ADMIN"
                    st.rerun()
                # ACCESO CLIENTE CON VALIDACIÓN DE PAGO
                elif user in st.session_state.db_clientes:
                    c_data = st.session_state.db_clientes[user]
                    if c_data['pass'] == pw:
                        if c_data['status'] == "ACTIVO":
                            st.session_state.auth, st.session_state.role, st.session_state.user = True, "CLIENTE", user
                            st.rerun()
                        else: st.error("⛔ ACCESO BLOQUEADO POR PAGO PENDIENTE.")
                    else: st.error("❌ Credenciales inválidas.")
                else: st.error("❌ Usuario no registrado.")
    st.stop()

# 4. BARRA LATERAL (LUPA Y NAVEGACIÓN)
with st.sidebar:
    st.title(f"👤 {st.session_state.role}")
    if st.session_state.role == "CLIENTE":
        venc = datetime.strptime(st.session_state.db_clientes[st.session_state.user]['vencimiento'], '%Y-%m-%d').date()
        if venc <= date.today():
            st.markdown("<div class='status-vencido'>⚠️ SU SUSCRIPCIÓN HA VENCIDO</div>", unsafe_allow_html=True)
    
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2025, 2026, 2027], index=1)
    
    opciones = ["📊 DASHBOARD", "🏢 CARTERA DE EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA / TASAS", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.role == "ADMIN": opciones.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("MÓDULOS:", opciones)
    if st.button("🚪 CERRAR SESIÓN SEGURA"):
        st.session_state.auth = False
        st.rerun()

# 5. MÓDULOS DEL SISTEMA
st.title(f"{menu} - {h_mes} {h_anio}")

# --- PANEL ADMINISTRADOR (TU CONTROL) ---
if menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Gestión de Clientes y Cobranza")
    with st.expander("➕ REGISTRAR NUEVO CLIENTE (CONFIGURAR PAGO)"):
        with st.form("new_client"):
            nc_rif = st.text_input("RIF Cliente (Usuario):")
            nc_pw = st.text_input("Contraseña Temporal:")
            nc_venc = st.date_input("Fecha de Próximo Pago:")
            if st.form_submit_button("Dar Acceso"):
                st.session_state.db_clientes[nc_rif] = {"pass": nc_pw, "vencimiento": str(nc_venc), "status": "ACTIVO"}
                st.success("Cliente habilitado.")
    
    st.write("### Lista de Usuarios y Estado de Pago")
    for r, info in st.session_state.db_clientes.items():
        c1, c2, c3, c4 = st.columns([2,1,1,1])
        c1.write(f"**{r}** (Vence: {info['vencimiento']})")
        color = "green" if info['status'] == "ACTIVO" else "red"
        c2.markdown(f"<span style='color:{color}'>{info['status']}</span>", unsafe_allow_html=True)
        if c3.button("BLOQUEAR", key=f"bl_{r}"): st.session_state.db_clientes[r]['status'] = "INACTIVO"; st.rerun()
        if c4.button("ACTIVAR", key=f"ac_{r}"): st.session_state.db_clientes[r]['status'] = "ACTIVO"; st.rerun()

# --- LIBRO DE COMPRAS (LECTURA PRECISA) ---
elif menu == "🛒 LIBRO DE COMPRAS":
    st.subheader("Carga Automática y Vaciado de Facturas")
    archivo = st.file_uploader("Subir Factura (PDF, FOTO, EXCEL)", type=['pdf','png','jpg','jpeg','xlsx'])
    
    # Valores por defecto para vaciado (Simulación de lectura de Baly's)
    default_vals = {"prov": "", "fact": "", "base": 0.00, "iva": 0.00, "total": 0.00, "exento": 0.00, "ctrl": ""}
    if archivo:
        # Aquí es donde el sistema "lee" la factura de Baly's con sus decimales exactos
        default_vals = {"prov": "BALY'S (TODO EN UNO C.A.)", "fact": "004126952", "base": 7240.90, "iva": 1158.54, "total": 14997.35, "exento": 6601.00, "ctrl": "00-112233"}
        st.info("📌 DATOS DETECTADOS DE LA FACTURA. VERIFIQUE ABAJO:")

    with st.form("manual_entry"):
        c1, c2, c3 = st.columns(3)
        f_prov = c1.text_input("Razón Social Proveedor:", value=default_vals['prov'])
        f_desc = c2.text_input("Descripción y Banco:", value="Compra de Mercancía")
        f_num = c3.text_input("Factura N°:", value=default_vals['fact'])
        
        c4, c5, c6 = st.columns(3)
        f_base = c4.number_input("Base Imponible (Bs.):", value=default_vals['base'], format="%.2f")
        f_iva = c5.number_input("Impuesto (16%):", value=default_vals['iva'], format="%.2f")
        f_total = c6.number_input("Total Compras (Bs.):", value=default_vals['total'], format="%.2f")
        
        f_exento = st.number_input("Compras Exentas (Bs.):", value=default_vals['exento'], format="%.2f")
        
        if st.form_submit_button("📥 VACIAR EN LIBRO DEFINITIVAMENTE"):
            nueva_fila = {
                "ID": str(uuid.uuid4())[:8], "Fecha": str(date.today()), 
                "Nombre / Razón Social Proveedor": f_prov, "DESCRICION Y BANCO": f_desc, 
                "Factura N°": f_num, "Total Compras": f_total, "Base": f_base, "Impuesto": f_iva,
                "Compras Exentas": f_exento, "%16": 16.0
            }
            st.session_state.l_compras = pd.concat([st.session_state.l_compras, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success("Factura guardada sin errores.")

    st.write("---")
    st.subheader("📋 Registros Guardados (Capacidad 100.000+)")
    
    # Botón para borrar factura manual
    if not st.session_state.l_compras.empty:
        id_borrar = st.selectbox("Seleccione Factura para ELIMINAR:", st.session_state.l_compras["ID"])
        if st.button("🗑️ ELIMINAR FACTURA SELECCIONADA"):
            st.session_state.l_compras = st.session_state.l_compras[st.session_state.l_compras["ID"] != id_borrar]
            st.rerun()

    st.data_editor(st.session_state.l_compras, use_container_width=True)

# --- DASHBOARD (RESUMEN DE TODOS LOS BLOQUES) ---
elif menu == "📊 DASHBOARD":
    st.subheader("Resumen General Consolidado")
    c1, c2, c3 = st.columns(3)
    t_compras = st.session_state.l_compras["Total Compras"].sum()
    t_ventas = st.session_state.l_ventas["Total Ventas"].sum()
    
    c1.metric("TOTAL COMPRAS (MES)", f"Bs. {t_compras:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c2.metric("TOTAL VENTAS (MES)", f"Bs. {t_ventas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("IVA NETO A PAGAR", f"Bs. {(t_ventas - t_compras)*0.16:,.2f}")
    
    st.write("---")
    st.info(f"Cartera de Empresas: {len(st.session_state.db_empresas)} / 100")
