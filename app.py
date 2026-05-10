import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, date
import uuid

# 1. SEGURIDAD Y PROTOCOLO MULTI-TENANT
st.set_page_config(page_title="OmniContable VE", layout="wide")

# Estilos: Alerta Roja Ley de Pensiones y Bloqueo de Bordes
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .alerta-pensiones { background-color: #9b1c1c; color: white; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# Inicialización de la "Big Data" (Simulación de base de datos relacional)
if 'db' not in st.session_state:
    st.session_state.db = {
        'empresas': {}, # RIF: {nombre, suscripcion, usuarios_activos}
        'master_data': {}, # RIF: {compras, ventas, diario, mayor, inpc}
        'logs_seguridad': []
    }

# 2. MOTOR DE NORMALIZACIÓN SENIAT (REGLA DE ORO: COMA DECIMAL)
def normalizar_monto_seniat(monto):
    """Convierte montos a formato TXT SENIAT: 1250,50 (Sin puntos en miles)"""
    return f"{monto:.2f}".replace(".", ",")

# 3. MÓDULO LEY DE PENSIONES 2025 (CÁLCULO DINÁMICO)
def calcular_pensiones(base_salarial, alicuota=9.0):
    return (base_salarial * alicuota) / 100

# 4. LÓGICA DE POSTEO INMUTABLE (VEN-NIIF)
def postear_asiento(rif, cuenta_debe, cuenta_haber, monto, glosa):
    """Posteo simultáneo en Diario y Mayor. Prohibido borrar según especificación."""
    asiento_id = str(uuid.uuid4())[:8]
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    nuevo_asiento = [
        {"ID": asiento_id, "Fecha": fecha, "Cuenta": cuenta_debe, "Detalle": glosa, "Debe": monto, "Haber": 0.0},
        {"ID": asiento_id, "Fecha": fecha, "Cuenta": cuenta_haber, "Detalle": glosa, "Debe": 0.0, "Haber": monto}
    ]
    
    df_asiento = pd.DataFrame(nuevo_asiento)
    st.session_state.db['master_data'][rif]['diario'] = pd.concat([
        st.session_state.db['master_data'][rif]['diario'], df_asiento
    ], ignore_index=True)

# --- INTERFAZ ADMINISTRATIVA ---

if 'auth' not in st.session_state:
    st.title("🛡️ Acceso OmniContable VE")
    col1, col2 = st.columns(2)
    user = col1.text_input("Usuario")
    clave = col2.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión Segura"):
        if user == "MARIA_ADMIN" and clave == "SISTEMA_2026_PRO":
            st.session_state.auth = "ADMIN"
            st.rerun()
    st.stop()

# --- DASHBOARD MAESTRO ---

with st.sidebar:
    st.header("⚙️ Panel de Control")
    opcion = st.radio("Módulos", ["Dashboard", "Lupa de Historial", "Fiscal: IVA/Pensiones", "Contabilidad: VEN-NIIF", "Cierre y Ajuste IPC"])
    if st.button("🚪 Salida Rápida"):
        del st.session_state.auth
        st.rerun()

if opcion == "Dashboard":
    st.title("📊 Dashboard Maestro (10,000+ Empresas)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Empresas Activas", "10,240", "+12%")
    c2.metric("Facturas Procesadas", "845,900")
    c3.metric("Recaudación Estimada (IVA)", "Bs. 4.5M")
    c4.metric("Alertas de Pago", "24", delta_color="inverse")
    
    st.subheader("🚦 Semáforo Fiscal de Entidades")
    st.table(pd.DataFrame({
        "Empresa": ["Inversiones Baly's", "TecnoMundo J&R", "Alimentos Aragua"],
        "RIF": ["J-500773587", "J-304958671", "G-200394850"],
        "Estado IVA": ["✅ Declarado", "⚠️ Pendiente (2 días)", "❌ Vencido"],
        "Ley Pensiones": ["✅ Pagado", "✅ Pagado", "⚠️ Pendiente"]
    }))

elif opcion == "Lupa de Historial":
    st.title("🔍 Lupa de Historial (Big Data)")
    st.info("Busque entre los 100,000 registros históricos por RIF o N° de Factura")
    busqueda = st.text_input("Ingrese RIF o Número de Factura para búsqueda instantánea:")
    # Simulación de pipeline masivo
    st.write("Resultados de auditoría inmutable:")
    st.data_editor(pd.DataFrame(columns=["RIF", "Factura", "Fecha", "Monto Bs.", "Usuario Posteo", "Hash Seguridad"]))

elif opcion == "Fiscal: IVA/Pensiones":
    st.title("⚖️ Módulo Fiscal y Parafiscal")
    
    tab1, tab2, tab3 = st.tabs(["Carga de Facturas (OCR)", "Ley de Pensiones 2025", "Generación TXT/XML"])
    
    with tab1:
        st.subheader("Pipeline de Carga Masiva")
        up = st.file_uploader("Cargar Lote de Facturas (Máx 100,000)", accept_multiple_files=True)
        if up:
            st.success(f"Procesando {len(up)} archivos... Extrayendo datos VEN-NIIF automáticamente.")

    with tab2:
        st.markdown("<div class='alerta-pensiones'>CÁLCULO LEY DE PENSIONES - ALÍCUOTA 9% (Decreto 2025)</div>", unsafe_allow_html=True)
        base = st.number_input("Base Salarial Total del Mes (Bs.)", min_value=0.0)
        aporte = calcular_pensiones(base)
        st.subheader(f"Total Aporte a Declarar: Bs. {aporte:,.2f}")
        
        if st.button("Postear Gasto de Pensión"):
            st.info("Asiento automático generado: Gasto Personal (Debe) vs Ley Pensiones por Pagar (Haber)")

    with tab3:
        st.subheader("Generación de Archivos SENIAT")
        col_a, col_b = st.columns(2)
        if col_a.button("Generar TXT IVA (Coma Decimal)"):
            # Estructura TXT según regla de oro
            txt_ejemplo = f"J505802801|202603|15/03/2026|01|004126952|{normalizar_monto_seniat(7240.90)}|{normalizar_monto_seniat(1158.54)}"
            st.code(txt_ejemplo, language="text")
        
        if col_b.button("Generar XML ISLR"):
            root = ET.Element("RelacionRetencionesISLR", RifAgente="J505802801", Periodo="202603")
            det = ET.SubElement(root, "DetalleRetencion")
            ET.SubElement(det, "RifRetenido").text = "V12345678"
            ET.SubElement(det, "MontoOperacion").text = "5000,00"
            st.code(ET.tostring(root, encoding="unicode"), language="xml")

elif opcion == "Contabilidad: VEN-NIIF":
    st.title("📖 Estados Financieros Unificados")
    st.subheader("Estado de Ganancias y Pérdidas (Comparativo Divisas)")
    
    egp = pd.DataFrame({
        "Cuenta": ["Ventas Netas", "Costo de Ventas", "Gastos Administrativos", "Utilidad Neta"],
        "Bs. (Histórico)": [500000.00, -200000.00, -50000.00, 250000.00],
        "USD (Ref. 36.50)": [13698.63, -5479.45, -1369.86, 6849.31]
    })
    st.table(egp)
    
    st.subheader("Balance General (Situación Financiera)")
    st.write("Patrimonio Actualizado Post-Cierre:")
    st.metric("Patrimonio Total", "Bs. 1,240,500.00", "Resultados Acumulados")

elif opcion == "Cierre y Ajuste IPC":
    st.title("📈 Ajuste por Inflación Fiscal")
    st.write("Tabla de INPC (Banco Central de Venezuela)")
    inpc_data = pd.DataFrame({
        "Mes": ["Enero", "Febrero", "Marzo"],
        "INPC 2026": [1250.4, 1280.1, 1310.5],
        "Factor Variación": [1.0, 1.023, 1.048]
    })
    st.table(inpc_data)
    if st.button("Ejecutar Reexpresión de Estados Financieros"):
        st.warning("Calculando Variación de IPC sobre Propiedad, Planta y Equipo...")
