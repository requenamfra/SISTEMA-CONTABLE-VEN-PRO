🛡️ Especificación Técnica: OmniContable VE
Objetivo: SaaS Multitenant para >10,000 empresas con OCR masivo y cumplimiento VEN-NIIF.

1. Arquitectura y Seguridad Crítica
Acceso Diferenciado:

Administrador: Gestión de licencias, habilitar/deshabilitar RIFs, creación de usuarios adicionales para una misma empresa (trabajo colaborativo). No tiene acceso a data contable.

Cliente: Acceso total a módulos contables y fiscales de su entidad.

Seguridad: Protección contra Inyección SQL, cifrado SSL y Hashing SHA-256 para contraseñas.

Interfaz: 100% en Español con Logout rápido.

2. Reportes y Salidas Fiscales (SENIAT)
A. Formato Exacto TXT (Libro de IVA)
Regla de Oro: Separador pipe |, decimales con coma (,), sin separadores de miles.
RIF|Periodo|Fecha|TipoOp|TipoDoc|RifTercero|Factura|Control|Total|Base|IVA|Afectada|Ilicito|Alicuota|Exento
Ejemplo: J500773587|202605|09/05/2026|01|01|V22216898|004126952|00-45866314|8399,44|7240,90|1158,54|0|0|16|0

B. Estructura XML (Retenciones ISLR)
<RelacionRetencionesISLR RifAgente="J500773587" Periodo="202605">
    <DetalleRetencion>
        <RifRetenido>V22216898</RifRetenido>
        <NumeroFactura>004126952</NumeroFactura>
        <MontoOperacion>7240,90</MontoOperacion>
        <PorcentajeRetencion>3,00</PorcentajeRetencion>
    </DetalleRetencion>
</RelacionRetencionesISLR>
