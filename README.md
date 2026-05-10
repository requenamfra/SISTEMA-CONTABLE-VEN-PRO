# 🛡️ Especificación Técnica: OmniContable VE (SaaS Contable)

## 1. Arquitectura, Seguridad y Control de Acceso
El sistema debe implementar un esquema de **Multitenancy Estricto** y **Login Diferenciado**:

### A. Perfil Administrador Global (Control de Negocio)
- **Funciones**: Crear/Editar Empresas, Generar Usuarios Adicionales, Monitorear Vencimientos.
- **Restricción**: El Administrador NO puede ver libros contables, facturas ni estados financieros de los clientes (Privacidad de Data).
- **Listado de Clientes**: Tabla interactiva con columnas: RIF, Razón Social, Fecha Vencimiento, Estado (Habilitado/Deshabilitado).
- **Gestión de Usuarios**: Botón para resetear claves y vincular múltiples correos a un mismo RIF.

### B. Perfil Cliente / Contador (Operación)
- **Funciones**: Carga OCR (100k+), Libros Legales, Ley de Pensiones 2025, Exportación SENIAT.
- **Alertas Automáticas**: Al faltar **5 días** para el vencimiento, el sistema bloquea funciones secundarias y muestra un Banner de Advertencia Amarillo en el Dashboard.

### C. Seguridad Crítica (Zero-Leak)
- **Hashing**: Todas las contraseñas deben cifrarse usando `SHA-256` o `Bcrypt`. Prohibido texto plano.
- **Protección**: Middleware activo contra Inyección SQL y XSS. Certificado SSL obligatorio (HTTPS).
- **Interfaz**: 100% en Español. Logout mediante botón de "Salida Rápida" en barra lateral.
