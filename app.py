import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid

# 1. CONFIGURACIÓN DE SEGURIDAD Y BLOQUEO DE NAVEGACIÓN
st.set_page_config(page_title="VEN-PRO v400 - SISTEMA CONTABLE PROFESIONAL", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #f8f9fa !important; }
    .alerta-pago { color: #FF0000; font-weight: bold; font-size: 20px; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #e9ecef; border-radius: 5px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE BASE DE DATOS (MEMORIA MASIVA)
if 'db_master' not in st.session_state:
    st.session_state.auth = False
    st.session_state.db_clientes = {} # {rif: {pass, vencimiento, status}}
    st.session_state.cartera_empresas = [] # Cartera de hasta 100 empresas
    st.session_state.l_compras = pd.DataFrame(columns=["ID", "Fecha", "Nombre / Razón Social Proveedor", "DESCRICION Y BANCO", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"])
    st.session_state.l_ventas = pd.DataFrame(columns=["ID", "Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"])
    st.session_state.l_diario_mayor = pd.DataFrame(columns=["Fecha", "Cuenta (VEN-NIIF)", "Descripción", "Debe (Bs.)", "Haber (Bs.)", "Empresa"])
    st.session_state.parafiscales = pd.DataFrame(columns=["Fecha", "Tipo", "Monto", "Comprobante"])

# 3. ACCESO BLINDADO
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🛡️ INGRESO AL SISTEMA VEN-PRO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        with st.form("login"):
            u = st.text_input("USUARIO / RIF:").strip().upper()
            p = st.text_input("CONTRASEÑA:", type="password").strip()
            if st.form_submit_button("INGRESAR"):
                if u == "MARIA" and p == "ADMIN2026":
                    st.session_state.auth, st.session_state.role = True, "ADMIN"
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]['pass'] == p:
                    if st.session_state.db_clientes[u]['status'] == "ACTIVO":
                        st.session_state.auth, st.session_state.role, st.session_state.user_id = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("🚫 ACCESO BLOQUEADO. PAGO PENDIENTE.")
                else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# 4. BARRA LATERAL (LUPA DE HISTORIAL + MENÚ)
with st.sidebar:
    st.title(f"⭐ {st.session_state.role}")
    if st.session_state.role == "CLIENTE":
        venc_dt = datetime.strptime(st.session_state.db_clientes[st.session_state.user_id]['vencimiento'], '%Y-%m-%d').date()
        if (venc_dt - date.today()).days <= 5:
            st.markdown(f"<p class='alerta-pago'>⚠️ PAGO VENCE EL: {venc_dt}</p>", unsafe_allow_html=True)

    st.subheader("🔍 LUPA DE HISTORIAL")
    mes_h = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    anio_h = st.selectbox("Año", [2024, 2025, 2026])

    menu = ["📊 DASHBOARD", "🏢 CARTERA EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏢 PARAFISCALES", "🏛️ ALCALDÍA", "📤 SENIAT (XML/TXT)"]
    if st.session_state.role == "ADMIN": menu.insert(1, "👑 PANEL ADMINISTRADOR")
    
    sel = st.radio("MÓDULOS", menu)
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 5. MÓDULOS DE ADMINISTRADOR
if sel == "👑 PANEL ADMINISTRADOR":
    st.header("Gestión de Clientes y Suscripciones")
    with st.form("new_client"):
        c1, c2, c3 = st.columns(3)
        rif = c1.text_input("RIF Cliente:")
        clave = c2.text_input("Contraseña:")
        venc = c3.date_input("Fecha de Pago Mensual:")
        if st.form_submit_button("REGISTRAR CLIENTE Y DAR ACCESO"):
            st.session_state.db_clientes[rif] = {"pass": clave, "vencimiento": str(venc), "status": "ACTIVO"}
            st.success("Cliente habilitado.")

    st.write("### Lista de Clientes y Estado de Pago")
    for r, info in st.session_state.db_clientes.items():
        col1, col2 = st.columns([3, 1])
        status_color = "🟢" if info['status'] == "ACTIVO" else "🔴"
        col1.write(f"{status_color} **{r}** - Vencimiento: {info['vencimiento']}")
        if col2.button("BLOQUEAR / DESBLOQUEAR", key=r):
            st.session_state.db_clientes[r]['status'] = "INACTIVO" if info['status'] == "ACTIVO" else "ACTIVO"
            st.rerun()

# 6. CARTERA DE EMPRESAS (MÁX 100)
elif sel == "🏢 CARTERA EMPRESAS":
    st.header("Gestión de Cartera (Capacidad: 100 Empresas)")
    with st.form("empresa"):
        e1, e2 = st.columns(2)
        nom_e = e1.text_input("Nombre de la Empresa:")
        rif_e = e2.text_input("RIF:")
        if st.form_submit_button("GUARDAR EN CARTERA"):
            if len(st.session_state.cartera_empresas) < 100:
                st.session_state.cartera_empresas.append({"Nombre": nom_e, "RIF": rif_e})
            else: st.error("Límite de 100 empresas alcanzado.")
    st.table(pd.DataFrame(st.session_state.cartera_empresas))

# 7. LIBRO DE COMPRAS (LECTURA PRECISA + VACIADO)
elif sel == "🛒 LIBRO DE COMPRAS":
    st.header(f"🛒 Libro de Compras - {mes_h} {anio_h}")
    up = st.file_uploader("CARGAR FACTURAS (PDF, JPEG, PNG, EXCEL)", type=['pdf','png','jpg','jpeg','xlsx'])
    
    st.subheader("Carga y Vaciado Manual")
    with st.form("vaciado_compras"):
        c1, c2, c3, c4 = st.columns(4)
        prov = c1.text_input("Razón Social Proveedor")
        desc = c2.text_input("DESCRICIÓN Y BANCO")
        fact = c3.text_input("Factura N°")
        cont = c4.text_input("N° Control")
        
        c5, c6, c7, c8 = st.columns(4)
        base = c5.number_input("Base Imponible (Bs.)", format="%.2f")
        iva = c6.number_input("Impuesto %16 (Bs.)", format="%.2f")
        exento = c7.number_input("Compras Exentas (Bs.)", format="%.2f")
        total = c8.number_input("Total Compras (Bs.)", format="%.2f")
        
        if st.form_submit_button("📥 CARGAR FACTURA AL SISTEMA"):
            row = {"ID": str(uuid.uuid4())[:6], "Nombre / Razón Social Proveedor": prov, "DESCRICION Y BANCO": desc, "Factura N°": fact, "Nº Control": cont, "Base": base, "Impuesto": iva, "Compras Exentas": exento, "Total Compras": total, "Fecha": str(date.today())}
            st.session_state.l_compras = pd.concat([st.session_state.l_compras, pd.DataFrame([row])], ignore_index=True)
            st.success("Factura vaciada y guardada.")

    st.write("### Historial Masivo")
    if not st.session_state.l_compras.empty:
        id_borrar = st.selectbox("Seleccione ID para borrar factura errónea:", st.session_state.l_compras["ID"])
        if st.button("🗑️ BORRAR MANUALMENTE"):
            st.session_state.l_compras = st.session_state.l_compras[st.session_state.l_compras["ID"] != id_borrar]
            st.rerun()
    st.data_editor(st.session_state.l_compras, use_container_width=True)

# 8. DASHBOARD RESUMEN
elif sel == "📊 DASHBOARD":
    st.header("Resumen General de Bloques")
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Compras", f"Bs. {st.session_state.l_compras['Total Compras'].sum():,.2f}")
    k2.metric("Total Ventas", f"Bs. {st.session_state.l_ventas['Total Ventas'].sum():,.2f}")
    k3.metric("Empresas en Cartera", len(st.session_state.cartera_empresas))
    
    st.info("Todos los movimientos de meses anteriores están disponibles mediante la Lupa de Historial.")

# 9. PARAFISCALES Y ALCALDÍA
elif sel in ["🏢 PARAFISCALES", "🏛️ ALCALDÍA"]:
    st.header(f"Gestión de Pagos: {sel}")
    up_p = st.file_uploader("Subir Comprobante (IVSS, FAOV, INCES, ASEO, IAE, etc.)")
    st.data_editor(pd.DataFrame(columns=["Tipo", "Fecha Pago", "Monto (Bs.)", "Referencia"]), num_rows="dynamic", use_container_width=True)
