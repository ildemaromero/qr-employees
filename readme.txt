configuración para apache
<IfModule mod_rewrite.c>
RewriteEngine On

RewriteRule ^sistema-qr(/.*)?$ http://127.0.0.1:8000/sistema-qr$1 [P,L]
RequestHeader set X-Forwarded-Proto "https"
RequestHeader set X-Forwarded-Host "grupobyp.com"
</IfModule>