# SISTEMA-CONTABLE-VEN-PRO
Sistema Integral de Gestión Contable, Fiscal y Parafiscal VEN-PRO. Diseñado para contribuyentes. Incluye módulos de Alcaldía Girardot, Parafiscales y Control de Libros Legales.
## 📤 Especificación Técnica: Exportación XML ISLR
El sistema debe generar un archivo con extensión `.xml` para la declaración de retenciones, siguiendo esta estructura exacta:

### Plantilla de Referencia (Ejemplo Factura 004126952)
| Campo | Valor de Origen |
| :--- | :--- |
| **RifAgente** | J500773587 (Baly's Todo en Uno C.A.) |
| **RifRetenido** | V22216898 (Briggy Garcia) |
| **MontoOperacion** | 7240,90 (Base Imponible) |

### Código de Estructura XML:
<RelacionRetencionesISLR RifAgente="J500773587" Periodo="202605">
    <DetalleRetencion>
        <RifRetenido>V22216898</RifRetenido>
        <NumeroFactura>004126952</NumeroFactura>
        <NumeroControl>00-45866314</NumeroControl>
        <FechaOperacion>08/05/2026</FechaOperacion>
        <CodigoConcepto>001</CodigoConcepto>
        <MontoOperacion>7240,90</MontoOperacion>
        <PorcentajeRetencion>3,00</PorcentajeRetencion>
    </DetalleRetencion>
</RelacionRetencionesISLR>

> **Nota Crítica para el Programador:** Es obligatorio el uso de la **coma (,)** como separador decimal en los montos. No incluir separadores de miles.
> # Función para cumplir con la Regla de Oro del SENIAT
def formato_seniat(monto):
    # Formatea a 2 decimales, cambia punto por coma y elimina puntos de miles
    return "{:.2f}".format(monto).replace(".", ",")

# Ejemplo de salida esperada:
# J500773587|202605|08/05/2026|01|01|V22216898|004126952|00-45866314|8399,44|7240,90|1158,54|0|0|16|0
---

## 📄 Especificación Técnica: Exportación TXT IVA
El sistema debe generar un archivo plano `.txt` para los Libros de Compra y Venta, utilizando el carácter **pipe (|)** como separador único.

### Reglas de Oro (Validación SENIAT):
* **Separador Decimal**: Utilizar siempre **coma (,)**.
* **Separador de Miles**: **PROHIBIDO**. El sistema debe limpiar cualquier punto en los miles antes de exportar.
* **Formato de RIF**: Mayúsculas, sin guiones ni espacios (Ej: J500773587).

### Ejemplo de Estructura de Línea:
`J500773587|202605|08/05/2026|01|01|V22216898|004126952|00-45866314|8399,44|7240,90|1158,54|0|0|16|0`

### Lógica de Sincronización:
Al procesar facturas como la de **BALY'S TODO EN UNO C.A.** (RIF J500773587), el sistema debe mapear automáticamente:
* **Base Imponible**: 7240,90.
* **IVA (16%)**: 1158,54.
* **Total**: 14997,35.
* ---

## 🚀 Fase Final: Pase a Producción (Go-Live)
Esta sección dicta las reglas para el despliegue oficial del sistema.

### 1. Sanitización de Datos
* **Data Purge:** Antes del lanzamiento, se debe vaciar la base de datos de registros de prueba (facturas, asientos y empresas ficticias).
* **Reset de IDs:** Los contadores de asientos contables y números de control deben iniciar en 1.

### 2. Seguridad y Onboarding
* **Seguridad:** Activación obligatoria de SSL, Backups diarios y Firewall.
* **Tour de Usuario:** Implementar una guía interactiva que explique los módulos de OCR, Parafiscales y Exportación SENIAT al primer ingreso de cada cliente.
