import os
from django.core.wsgi import get_wsgi_application
from werkzeug.middleware.proxy_fix import ProxyFix  # ✅ добавляем

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KUAMWebSite.settings')

application = get_wsgi_application()

# Убедитесь, что ProxyFix применяется после get_wsgi_application
application = ProxyFix(application, x_for=1, x_proto=1)
