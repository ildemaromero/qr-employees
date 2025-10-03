# 📇 Sistema QR para Empleados

Este proyecto tiene como objetivo la **gestión y generación de códigos QR para empleados**, los cuales pueden ser **exportados para la creación de carnets**. Cada código QR generado contiene un enlace único que permite acceder a una **descripción detallada del empleado**, útil para identificación, validación o control de acceso.

## 🔧 Configuración Apache

Para redireccionar correctamente las solicitudes al backend, se recomienda agregar la siguiente configuración en Apache:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On

  RewriteRule ^sistema-qr(/.*)?$ http://127.0.0.1:8000/sistema-qr$1 [P,L]
  RequestHeader set X-Forwarded-Proto "https"
  RequestHeader set X-Forwarded-Host "grupobyp.com"
</IfModule>
