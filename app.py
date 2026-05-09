import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
import re

# 1. CONFIGURACIÓN DE SEGURIDAD Y ESTILO
st.set_page_config(page_title="VEN-PRO v500", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #f4f7f6; }
    .alerta-pago { color: #FF0000; font-weight: bold; font-size: 20px; animation: blinker 1.2s linear infinite; text-align: center; }
    @keyframes blinker { 50% { opacity: 0; } }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE LA BASE DE DATOS MASIVA (100.000+ Registros)
if 'init' not in st.session_state:
    st.session_state.init = True
    st.session_state.auth = False
    st.session_state.role = None
    st.session_state.user_active = None
    st.session_state.db_clientes = {} # {rif: {pass, vencimiento, status}}
    st.session_state.cartera_empresas = pd.DataFrame(columns=["RIF", "Nombre de Empresa", "Contacto", "Estado"])
    st.session_state.l_compras = pd.DataFrame(columns=["ID", "Fecha", "Nombre / Razón Social Proveedor", "DESCRICION Y BANCO", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"])
    st.session_state.l_ventas = pd.DataFrame(columns=["Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"])
    st.session_state.diario_mayor = pd.DataFrame(columns=["Fecha", "Cuenta (VEN-NIIF)", "Detalle", "Debe (Bs.)", "Haber (Bs.)"])

# 3. NÚCLEO DE EXTRACCIÓN DINÁMICA (LECTOR INTELIGENTE)
def lector_inteligente(file):
    # Simulación de extracción dinámica por patrones (Regex)
    # En un entorno real, aquí conectarías un OCR como Tesseract o AWS Textract
    texto_simulado = "Factura 001 Proveedor Global C.A. RIF J-123456 Base: 1050,55 IVA: 168,09 Total: 1218,64"
    
    # Captura montos con decimales (coma)
    montos = re.findall(r'\d+,\d{2}', texto_simulado)
    return {
        "prov": "EXTRACCIÓN DINÁMICA CLOUD",
        "fact": str(uuid.uuid4().int)[:8],
        "base": float(montos[0].replace(',','.')) if montos else 0.00,
        "iva": float(montos[1].replace(',','.')) if len(montos)>1 else 0.00,
        "total": float(montos[2].replace(',','.')) if len(montos)>2 else 0.00
    }

# 4. SISTEMA DE ACCESO (LOGIN)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🔑 SISTEMA CONTABLE VEN-PRO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        u = st.text_input("USUARIO / RIF:").strip().upper()
        p = st.text_input("CONTRASEÑA:", type="password").strip()
        if st.button("🛡️ INGRESAR"):
            if u == "MARIA" and p == "ADMIN2026":
                st.session_state.auth, st.session_state.role = True, "ADMIN"
                st.rerun()
            elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]['pass'] == p:
                if st.session_state.db_clientes[u]['status'] == "ACTIVO":
                    st.session_state.auth, st.session_state.role, st.session_state.user_active = True, "CLIENTE", u
                    st.rerun()
                else: st.error("🚫 ACCESO BLOQUEADO. CONTACTE AL ADMINISTRADOR.")
            else: st.error("❌ Datos incorrectos. Verifique Mayúsculas.")
    st.stop()

# 5. ESTRUCTURA PRINCIPAL (SIDEBAR)
with st.sidebar:
    st.title(f"⭐ {st.session_state.role}")
    if st.session_state.role == "CLIENTE":
        info = st.session_state.db_clientes[st.session_state.user_active]
        venc = datetime.strptime(info['vencimiento'], "%Y-%m-%d").date()
        if (venc - date.today()).days <= 5:
            st.markdown(f"<p class='alerta-pago'>⚠️ SU MES SE ESTÁ ACABANDO<br>VENCE: {venc}</p>", unsafe_allow_html=True)

    st.subheader("🔍 LUPA DE HISTORIAL")
    mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    anio = st.selectbox("Año", [2024, 2025, 2026])

    menu = ["📊 DASHBOARD", "🏢 CARTERA EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏢 PARAFISCALES", "🏛️ ALCALDÍA", "📤 SENIAT (XML/TXT)"]
    if st.session_state.role == "ADMIN": menu.insert(1, "👑 PANEL ADMINISTRADOR")
    
    opcion = st.radio("MENÚ DE SISTEMA", menu)
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 6. MÓDULO ADMINISTRADOR (EL PODER DE MARÍA)
if opcion == "👑 PANEL ADMINISTRADOR":
    st.header("Control Maestro de Clientes")
    with st.form("registro_admin"):
        c1, c2, c3 = st.columns(3)
        n_rif = c1.text_input("RIF Cliente / Usuario:")
        n_pass = c2.text_input("Asignar Contraseña:")
        n_venc = c3.date_input("Fecha Vencimiento de Pago:")
        if st.form_submit_button("REGISTRAR Y DAR ACCESO"):
            st.session_state.db_clientes[n_rif] = {"pass": n_pass, "vencimiento": str(n_venc), "status": "ACTIVO"}
            st.success(f"Cliente {n_rif} activado correctamente.")

    st.subheader("Lista de Clientes Activos (Control de Pagos)")
    for r, d in st.session_state.db_clientes.items():
        col1, col2, col3 = st.columns([2, 1, 1])
        col1.write(f"**RIF:** {r} | **Vence:** {d['vencimiento']}")
        if col2.button("BLOQUEAR" if d['status']=="ACTIVO" else "ACTIVAR", key=r):
            st.session_state.db_clientes[r]['status'] = "INACTIVO" if d['status']=="ACTIVO" else "ACTIVO"
            st.rerun()

# 7. MÓDULO CARTERA DE EMPRESAS (MÁX 100)
elif opcion == "🏢 CARTERA EMPRESAS":
    st.header("Registro de Cartera (Máx 100 Empresas)")
    with st.expander("➕ REGISTRAR NUEVA EMPRESA"):
        with st.form("form_empresa"):
            e1, e2 = st.columns(2)
            e_rif = e1.text_input("RIF de la Empresa:")
            e_nom = e2.text_input("Razón Social:")
            if st.form_submit_button("GUARDAR EN CARTERA"):
                if len(st.session_state.cartera_empresas) < 100:
                    nueva_e = pd.DataFrame([{"RIF": e_rif, "Nombre de Empresa": e_nom, "Estado": "Activo"}])
                    st.session_state.cartera_empresas = pd.concat([st.session_state.cartera_empresas, nueva_e], ignore_index=True)
                    st.success("Empresa añadida.")
    st.write("### Empresas bajo tu Contabilidad")
    st.dataframe(st.session_state.cartera_empresas, use_container_width=True)

# 8. MÓDULO COMPRAS (LECTOR INTELIGENTE Y VACIADO)
elif opcion == "🛒 LIBRO DE COMPRAS":
    st.header(f"🛒 Compras - {mes} {anio}")
    
    # BOTÓN DE CARGA
    files = st.file_uploader("CARGAR FACTURAS (MULTIPLE)", accept_multiple_files=True, type=['pdf','png','jpg','jpeg','xlsx'])
    
    if files:
        for f in files:
            datos = lector_inteligente(f)
            st.write(f"🔍 Leído: {f.name}")
            
            # PARTE DE CARGA MANUAL REFLEJADA
            with st.form(key=f"form_{f.name}"):
                c1, c2, c3 = st.columns(3)
                v_prov = c1.text_input("Proveedor", value=datos['prov'])
                v_fact = c2.text_input("Factura N°", value=datos['fact'])
                v_base = c3.number_input("Base (Bs.)", value=datos['base'], format="%.2f")
                
                c4, c5, c6 = st.columns(3)
                v_iva = c4.number_input("Impuesto %16", value=datos['iva'], format="%.2f")
                v_total = c5.number_input("Total Compras", value=datos['total'], format="%.2f")
                v_exento = c6.number_input("Exento", value=0.00, format="%.2f")
                
                if st.form_submit_button("📥 VACIAR A TABLA DEFINITIVAMENTE"):
                    nueva_f = {"ID": str(uuid.uuid4())[:6], "Fecha": str(date.today()), "Nombre / Razón Social Proveedor": v_prov, "Factura N°": v_fact, "Base": v_base, "Impuesto": v_iva, "Total Compras": v_total, "Compras Exentas": v_exento, "DESCRICION Y BANCO": "Compra Mercancía"}
                    st.session_state.l_compras = pd.concat([st.session_state.l_compras, pd.DataFrame([nueva_f])], ignore_index=True)
                    st.toast("Factura guardada.")

    st.subheader("Tabla de Control Masivo (Historial)")
    # Borrado manual
    if not st.session_state.l_compras.empty:
        id_del = st.selectbox("ID para borrar:", st.session_state.l_compras["ID"])
        if st.button("🗑️ ELIMINAR REGISTRO"):
            st.session_state.l_compras = st.session_state.l_compras[st.session_state.l_compras["ID"] != id_del]
            st.rerun()
            
    st.data_editor(st.session_state.l_compras, use_container_width=True)

# 9. DASHBOARD (RESUMEN DE BLOQUES)
elif opcion == "📊 DASHBOARD":
    st.header(f"Resumen General - {mes}")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("FACTURAS TOTALES", len(st.session_state.l_compras))
    k2.metric("TOTAL COMPRAS (Bs.)", f"{st.session_state.l_compras['Total Compras'].sum():,.2f}")
    k3.metric("IVA POR PAGAR", f"{st.session_state.l_compras['Impuesto'].sum():,.2f}")
    k4.metric("EMPRESAS", len(st.session_state.cartera_empresas))
    
    st.write("---")
    st.write("### Flujo de Caja")
    st.bar_chart(st.session_state.l_compras["Total Compras"])
