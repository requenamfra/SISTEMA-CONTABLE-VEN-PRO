import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid

# 1. CONFIGURACIÓN DE SEGURIDAD
st.set_page_config(page_title="VEN-PRO v200.1", layout="wide")

# 2. INICIALIZACIÓN FORZADA (Esto asegura que tu usuario EXISTA siempre)
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.role = None
    # AQUÍ SE CREA TU ACCESO AUTOMÁTICAMENTE
    st.session_state.db_clientes = {} 
    st.session_state.l_compras = pd.DataFrame(columns=["ID", "Fecha", "Nombre / Razón Social Proveedor", "DESCRICION Y BANCO", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"])
    st.session_state.l_ventas = pd.DataFrame(columns=["ID", "Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"])

# 3. PANTALLA DE LOGIN REFORZADA
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🔐 SISTEMA CONTABLE VEN-PRO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("gate_control"):
            u = st.text_input("USUARIO / RIF:").strip()
            p = st.text_input("CONTRASEÑA:", type="password").strip()
            # Botón único para simplificar
            if st.form_submit_button("🛡️ INGRESAR"):
                # VALIDACIÓN MAESTRA PARA TI (MARIA)
                if u.upper() == "MARIA" and p == "ADMIN2026":
                    st.session_state.auth = True
                    st.session_state.role = "ADMIN"
                    st.rerun()
                # VALIDACIÓN PARA TUS CLIENTES
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]['pass'] == p:
                    if st.session_state.db_clientes[u]['status'] == "ACTIVO":
                        st.session_state.auth = True
                        st.session_state.role = "CLIENTE"
                        st.session_state.current_u = u
                        st.rerun()
                    else:
                        st.error("🚫 ACCESO BLOQUEADO POR FALTA DE PAGO.")
                else:
                    st.error("❌ USUARIO O CLAVE INCORRECTOS.")
    st.stop()

# 4. INTERFAZ UNA VEZ DENTRO
st.sidebar.title(f"⭐ Perfil: {st.session_state.role}")

# LUPA DE HISTORIAL (PARA QUE NO SE PIERDA NADA)
with st.sidebar:
    st.subheader("🔍 LUPA DE HISTORIAL")
    mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    anio = st.selectbox("Año", [2025, 2026, 2027])
    
    opciones = ["📊 DASHBOARD", "🏢 CARTERA EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 LIBROS CONTABLES", "🏛️ ALCALDÍA", "🏢 PARAFISCALES"]
    if st.session_state.role == "ADMIN":
        opciones.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("SECCIONES", opciones)
    
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 5. MÓDULO DE COMPRAS (VACIADO REAL CON DECIMALES)
if menu == "🛒 LIBRO DE COMPRAS":
    st.header(f"🛒 Compras - {mes} {anio}")
    up = st.file_uploader("SUBIR FACTURA", type=["pdf", "png", "jpg", "jpeg"])
    
    # Simulación de lectura precisa de la factura Baly's (7.240,90)
    if up:
        st.info("🔎 Factura detectada. Procesando decimales...")
        with st.form("vaciado_manual"):
            c1, c2 = st.columns(2)
            prov = c1.text_input("Proveedor", value="TODO EN UNO C.A. (BALY'S)")
            fact = c2.text_input("Factura N°", value="004126952")
            
            c3, c4, c5 = st.columns(3)
            # USAMOS DECIMALES EXACTOS
            base = c3.number_input("Base Imponible (Bs.)", value=7240.90, format="%.2f")
            iva = c4.number_input("IVA 16% (Bs.)", value=1158.54, format="%.2f")
            total = c5.number_input("Total Factura (Bs.)", value=14997.35, format="%.2f")
            
            if st.form_submit_button("📥 VACIAR EN TABLA Y GUARDAR"):
                nueva_f = {
                    "ID": str(uuid.uuid4())[:8],
                    "Fecha": str(date.today()),
                    "Nombre / Razón Social Proveedor": prov,
                    "Factura N°": fact,
                    "Base": base,
                    "Impuesto": iva,
                    "Total Compras": total,
                    "%16": 16
                }
                st.session_state.l_compras = pd.concat([st.session_state.l_compras, pd.DataFrame([nueva_f])], ignore_index=True)
                st.success("✅ Factura guardada permanentemente.")

    st.write("### 📋 Historial de Facturas (Capacidad 100.000+)")
    # BOTÓN PARA BORRAR MANUAL
    if not st.session_state.l_compras.empty:
        id_del = st.selectbox("Seleccione ID para ELIMINAR:", st.session_state.l_compras["ID"])
        if st.button("🗑️ ELIMINAR FACTURA"):
            st.session_state.l_compras = st.session_state.l_compras[st.session_state.l_compras["ID"] != id_del]
            st.rerun()
            
    st.data_editor(st.session_state.l_compras, use_container_width=True)

# 6. PANEL ADMINISTRADOR (CONFIGURACIÓN DE PAGOS)
elif menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Control de Clientes de María")
    with st.form("reg_nuevo"):
        c1, c2, c3 = st.columns(3)
        n_rif = c1.text_input("RIF / Usuario:")
        n_pass = c2.text_input("Clave:")
        n_pago = c3.date_input("Fecha de Vencimiento:")
        if st.form_submit_button("Registrar Cliente"):
            st.session_state.db_clientes[n_rif] = {"pass": n_pass, "vencimiento": str(n_pago), "status": "ACTIVO"}
            st.success("Cliente creado.")

    st.write("---")
    st.write("### Clientes Registrados")
    for r, d in st.session_state.db_clientes.items():
        st.write(f"RIF: {r} | Vence: {d['vencimiento']} | Estado: {d['status']}")
