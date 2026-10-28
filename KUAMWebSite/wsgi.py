import os
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.wsgi import get_wsgi_application
from werkzeug.middleware.proxy_fix import ProxyFix  # ✅ добавляем

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KUAMWebSite.settings')

application = get_wsgi_application()

# Waitress does not serve Django static files itself. In the project's current
# DEBUG mode this wrapper keeps /static/ working with serve.py as well as with
# Django's development server. Production should still serve STATIC_ROOT via
# the reverse proxy after collectstatic.
if settings.DEBUG:
    application = StaticFilesHandler(application)

# Убедитесь, что ProxyFix применяется после get_wsgi_application
application = ProxyFix(application, x_for=1, x_proto=1)
