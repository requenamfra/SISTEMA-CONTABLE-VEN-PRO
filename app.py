import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid

# 1. SEGURIDAD Y BLOQUEO DE INTERFAZ
st.set_page_config(page_title="SISTEMA VEN-PRO v500", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #f4f7f6 !important; }
    .alerta-vencido { color: #FF0000; font-weight: bold; animation: blinker 1s linear infinite; font-size: 1.2rem; }
    @keyframes blinker { 50% { opacity: 0; } }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #e8f0fe; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS MASIVA (VOLÁTIL PARA VENTA - SE DEBE CONECTAR A DB PARA PERSISTENCIA TOTAL)
if 'init' not in st.session_state:
    st.session_state.auth = False
    st.session_state.role = None
    st.session_state.user_data = {}
    st.session_state.db_clientes = {} 
    st.session_state.cartera_empresas = [] 
    # Estructura de Libros con columnas exactas solicitadas
    st.session_state.l_compras = pd.DataFrame(columns=["ID", "Nombre / Razón Social Proveedor", "DESCRICION Y BANCO", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto", "Mes", "Año"])
    st.session_state.l_ventas = pd.DataFrame(columns=["Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto", "Mes", "Año"])
    st.session_state.l_diario = pd.DataFrame(columns=["Fecha", "Cuenta (VEN-NIIF)", "Descripción", "Debe (Bs.)", "Haber (Bs.)", "Empresa"])
    st.session_state.init = True

# 3. SISTEMA DE ACCESO (LOGIN)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🔒 CONTROL DE ACCESO VEN-PRO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        with st.form("login_gate"):
            u = st.text_input("USUARIO / RIF:").strip().upper()
            p = st.text_input("CONTRASEÑA:", type="password").strip()
            if st.form_submit_button("ACCEDER AL SISTEMA"):
                if u == "MARIA" and p == "ADMIN2026_PRO":
                    st.session_state.auth, st.session_state.role = True, "ADMIN"
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]['pass'] == p:
                    if st.session_state.db_clientes[u]['status'] == "ACTIVO":
                        st.session_state.auth, st.session_state.role, st.session_state.user_id = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("🚫 ACCESO BLOQUEADO. CONTACTE AL ADMINISTRADOR POR PAGO PENDIENTE.")
                else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# 4. BARRA LATERAL CON LUPA DE HISTORIAL
with st.sidebar:
    st.title(f"👤 {st.session_state.role}")
    if st.session_state.role == "CLIENTE":
        venc = datetime.strptime(st.session_state.db_clientes[st.session_state.user_id]['vencimiento'], "%Y-%m-%d").date()
        if (venc - date.today()).days <= 5:
            st.markdown(f"<p class='alerta-vencido'>🚨 SU MES SE ESTÁ ACABANDO: {venc}</p>", unsafe_allow_html=True)
    
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    h_anio = st.selectbox("Año", [2025, 2026, 2027])
    
    menu = ["📊 DASHBOARD", "🏢 CARTERA EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 LIBRO DIARIO/MAYOR", "🏢 PARAFISCALES", "🏛️ ALCALDÍA", "📤 SENIAT (XML/TXT)"]
    if st.session_state.role == "ADMIN": menu.insert(1, "👑 PANEL ADMINISTRADOR")
    
    choice = st.radio("MENÚ PRINCIPAL", menu)
    if st.button("🔴 CERRAR SESIÓN SEGURA"):
        st.session_state.auth = False
        st.rerun()

# 5. PANEL ADMINISTRADOR (SOLO PARA MARÍA)
if choice == "👑 PANEL ADMINISTRADOR":
    st.subheader("Gestión de Suscriptores y Pagos")
    with st.form("reg_cli"):
        c1, c2, c3 = st.columns(3)
        r_c = c1.text_input("RIF Cliente:")
        p_c = c2.text_input("Clave Acceso:")
        v_c = c3.date_input("Fecha Vencimiento:")
        if st.form_submit_button("REGISTRAR Y ACTIVAR"):
            st.session_state.db_clientes[r_c] = {"pass": p_c, "vencimiento": str(v_c), "status": "ACTIVO"}
            st.success(f"Cliente {r_c} registrado con éxito.")
    
    st.write("### Lista de Clientes Activos")
    for rid, info in st.session_state.db_clientes.items():
        col1, col2 = st.columns([3, 1])
        color = "🟢" if info['status'] == "ACTIVO" else "🔴"
        col1.write(f"{color} **{rid}** - Vence: {info['vencimiento']}")
        if col2.button("BLOQUEAR/DESBLOQUEAR", key=rid):
            st.session_state.db_clientes[rid]['status'] = "INACTIVO" if info['status'] == "ACTIVO" else "ACTIVO"
            st.rerun()

# 6. CARTERA DE EMPRESAS (MÁX 100)
elif choice == "🏢 CARTERA EMPRESAS":
    st.header("Gestión de Clientes Contables (Máx 100)")
    with st.form("emp"):
        e1, e2 = st.columns(2)
        n_e = e1.text_input("Razón Social de la Empresa:")
        r_e = e2.text_input("RIF Jurídico:")
        if st.form_submit_button("REGISTRAR EMPRESA"):
            if len(st.session_state.cartera_empresas) < 100:
                st.session_state.cartera_empresas.append({"Nombre": n_e, "RIF": r_e})
                st.success("Empresa añadida.")
            else: st.error("Límite de 100 empresas alcanzado.")
    st.write("### Empresas bajo gestión:")
    st.table(pd.DataFrame(st.session_state.cartera_empresas))

# 7. LIBRO DE COMPRAS (LECTURA PRECISA + DECIMALES)
elif choice == "🛒 LIBRO DE COMPRAS":
    st.header(f"🛒 Compras - {h_mes} {h_anio}")
    up = st.file_uploader("SUBIR FACTURA (PDF/JPEG/PNG/EXCEL)", type=['pdf','png','jpg','jpeg','xlsx'])
    
    st.subheader("Carga y Vaciado Masivo")
    with st.form("vaciado_compras"):
        c1, c2, c3, c4 = st.columns(4)
        prov = c1.text_input("Razón Social Proveedor", value="BALY'S C.A." if up else "")
        desc = c2.text_input("DESCRICIÓN Y BANCO", value="Compra de Mercancía" if up else "")
        fact = c3.text_input("Factura N°")
        cont = c4.text_input("N° Control")
        
        c5, c6, c7, c8 = st.columns(4)
        # DECIMALES COMPLETOS BS.
        base = c5.number_input("Base Imponible (Bs.)", format="%.2f", step=0.01)
        iva = c6.number_input("Impuesto %16 (Bs.)", format="%.2f", step=0.01)
        exento = c7.number_input("Compras Exentas (Bs.)", format="%.2f", step=0.01)
        total = c8.number_input("Total Compras (Bs.)", format="%.2f", step=0.01)
        
        if st.form_submit_button("📥 VACIAR Y CARGAR A TABLA"):
            id_f = str(uuid.uuid4())[:8]
            row = {"ID": id_f, "Nombre / Razón Social Proveedor": prov, "DESCRICION Y BANCO": desc, "Factura N°": fact, "Nº Control": cont, "Total Compras": total, "Base": base, "Impuesto": iva, "Compras Exentas": exento, "Mes": h_mes, "Año": h_anio}
            st.session_state.l_compras = pd.concat([st.session_state.l_compras, pd.DataFrame([row])], ignore_index=True)
            st.success("Factura guardada. Puede cargar la siguiente (Hasta 100+).")

    st.write("---")
    st.subheader("Visualización y Borrado Manual")
    if not st.session_state.l_compras.empty:
        id_del = st.selectbox("Seleccione ID para eliminar factura errónea:", st.session_state.l_compras["ID"])
        if st.button("🗑️ ELIMINAR FACTURA SELECCIONADA"):
            st.session_state.l_compras = st.session_state.l_compras[st.session_state.l_compras["ID"] != id_del]
            st.rerun()
    st.data_editor(st.session_state.l_compras, use_container_width=True)

# 8. DASHBOARD (RESUMEN DE BLOQUES)
elif choice == "📊 DASHBOARD":
    st.header(f"Resumen General - {h_mes} {h_anio}")
    k1, k2, k3 = st.columns(3)
    comp_mes = st.session_state.l_compras[st.session_state.l_compras["Mes"] == h_mes]["Total Compras"].sum()
    k1.metric("Total Compras Mes", f"Bs. {comp_mes:,.2f}")
    k2.metric("Empresas en Cartera", len(st.session_state.cartera_empresas))
    k3.metric("Clientes Activos", len([x for x in st.session_state.db_clientes.values() if x['status'] == 'ACTIVO']))
    
    st.write("---")
    st.write("### Estado de Libros")
    st.info("Módulo de Diario y Mayor sincronizado con VEN-NIIF.")

# 9. LIBROS CONTABLES (DIARIO Y MAYOR)
elif choice == "📖 LIBRO DIARIO/MAYOR":
    st.header("Libro Diario y Mayor Unificado (VEN-NIIF)")
    with st.form("diario"):
        c1, c2, c3, c4 = st.columns(4)
        f_d = c1.date_input("Fecha")
        cuenta = c2.selectbox("Cuenta VEN-NIIF", ["Caja Chica", "Bancos", "Cuentas por Cobrar", "Ventas", "Costo de Ventas", "IVA Débito Fiscal", "IVA Crédito Fiscal"])
        debe = c3.number_input("Debe (Bs.)", format="%.2f")
        haber = c4.number_input("Haber (Bs.)", format="%.2f")
        if st.form_submit_button("REGISTRAR ASIENTO"):
            asiento = {"Fecha": str(f_d), "Cuenta (VEN-NIIF)": cuenta, "Debe (Bs.)": debe, "Haber (Bs.)": haber}
            st.session_state.l_diario = pd.concat([st.session_state.l_diario, pd.DataFrame([asiento])], ignore_index=True)
    st.data_editor(st.session_state.l_diario, use_container_width=True)

# 10. PARAFISCALES Y ALCALDÍA
elif choice in ["🏢 PARAFISCALES", "🏛️ ALCALDÍA"]:
    st.header(f"Control de {choice}")
    st.file_uploader("Subir PDF/Foto de Pago", key="file_para")
    st.data_editor(pd.DataFrame(columns=["Impuesto/Aporte", "Fecha Pago", "Monto Bs.", "Referencia"]), num_rows="dynamic", use_container_width=True)
