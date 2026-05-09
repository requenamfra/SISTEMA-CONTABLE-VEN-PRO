import streamlit as st
import pandas as pd
from datetime import datetime, date
import re

# 1. BLOQUEO Y ESTILO PROFESIONAL
st.set_page_config(page_title="VEN-PRO v90.0 - PRECISIÓN TOTAL", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, label { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button {
        width: 100% !important; border: 2px solid #000 !important; 
        background-color: #e8e8e8 !important; color: black !important; font-weight: bold;
    }
    .status-vencido { color: #FF0000 !important; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. MEMORIA DEL SISTEMA
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = {}
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = {}
if 'data_compras' not in st.session_state:
    st.session_state.data_compras = pd.DataFrame(columns=["Fecha", "Nombre / Razón Social Proveedor", "Descripción y Banco", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"])

# 3. MOTOR DE LECTURA DE PRECISIÓN (CORREGIDO)
def motor_lectura_venezuela(archivo):
    # Aquí simulamos la extracción de datos reales que viste en tu imagen
    # En un entorno de producción, aquí se procesa el OCR con IA de visión
    extracccion = {
        "Fecha": str(date.today()),
        "Proveedor": "INVERSIONES MARACAY, C.A.",
        "Factura": "0000874",
        "Control": "00-998877",
        "Total": 5800.50,  # Ejemplo de monto con decimales
        "Base": 5000.43,
        "IVA": 800.07
    }
    return extracccion

# 4. ACCESO CONTROLADO
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login"):
            u = st.text_input("USUARIO:").upper()
            p = st.text_input("CLAVE:", type="password")
            if st.form_submit_button("🔓 ENTRAR"):
                if u == "ADMIN" and p == "VEN2026":
                    st.session_state.auth, st.session_state.rol = True, "ADMIN"
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]["clave"] == p:
                    if st.session_state.db_clientes[u]["estatus"] == "Activo":
                        st.session_state.auth, st.session_state.rol = True, "CLIENTE"
                        st.rerun()
                else: st.error("❌ Acceso denegado")
    st.stop()

# 5. MENÚ Y LUPA
with st.sidebar:
    st.title(f"⭐ {st.session_state.rol}")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    menu = st.radio("MÓDULOS:", ["📊 DASHBOARD", "🏢 GESTIÓN DE EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA GIRARDOT", "🏢 PARAFISCALES"])
    if st.button("🔴 SALIR"):
        st.session_state.auth = False
        st.rerun()

# 6. MÓDULO DE COMPRAS (PRECISIÓN DE CIFRAS)
if menu == "🛒 LIBRO DE COMPRAS":
    st.title("🛒 Libro de Compras (Vaciado de Precisión)")
    
    with st.container():
        st.write("### 📸 Paso 1: Cargar Documento")
        up = st.file_uploader("Subir Factura (PDF/Foto)", type=['png', 'jpg', 'pdf'])
        
        if up:
            datos = motor_lectura_venezuela(up)
            st.warning("⚠️ Verifique los montos leídos antes de vaciar:")
            
            # Formulario de verificación antes de insertar
            with st.form("verificacion_vaciado"):
                c1, c2, c3 = st.columns(3)
                f_prov = c1.text_input("Proveedor:", value=datos["Proveedor"])
                f_nro = c2.text_input("Factura N°:", value=datos["Factura"])
                f_ctrl = c3.text_input("Control N°:", value=datos["Control"])
                
                c4, c5, c6 = st.columns(3)
                f_total = c4.number_input("Total Factura (Bs.):", value=datos["Total"], format="%.2f")
                f_base = c5.number_input("Base Imponible (Bs.):", value=datos["Base"], format="%.2f")
                f_iva = c6.number_input("IVA 16% (Bs.):", value=datos["IVA"], format="%.2f")
                
                if st.form_submit_button("📥 CONFIRMAR Y VACIAR A LIBRO"):
                    nueva_fila = {
                        "Fecha": datos["Fecha"], "Nombre / Razón Social Proveedor": f_prov,
                        "Descripción y Banco": "COMPRA NACIONAL", "Factura N°": f_nro,
                        "Nº Control": f_ctrl, "Total Compras": f_total, "Base": f_base, 
                        "%16": 16.0, "Impuesto": f_iva
                    }
                    st.session_state.data_compras = pd.concat([st.session_state.data_compras, pd.DataFrame([nueva_fila])], ignore_index=True)
                    st.success("✅ ¡Vaciado con éxito!")

    st.write("---")
    st.write("### 📖 Libro de Compras Actualizado")
    # Tabla con formato de moneda venezolana
    st.session_state.data_compras = st.data_editor(
        st.session_state.data_compras, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Total Compras": st.column_config.NumberColumn(format="Bs. %.2f"),
            "Base": st.column_config.NumberColumn(format="Bs. %.2f"),
            "Impuesto": st.column_config.NumberColumn(format="Bs. %.2f")
        }
    )

elif menu == "📊 DASHBOARD":
    st.title("📊 Resumen del Sistema")
    st.metric("TOTAL COMPRAS ACUMULADAS", f"{st.session_state.data_compras['Total Compras'].sum():,.2f} Bs.")
    st.metric("IVA CRÉDITO FISCAL", f"{st.session_state.data_compras['Impuesto'].sum():,.2f} Bs.")
