from django.shortcuts import render
from django.conf import settings

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Разрешаем админку
        if request.path.startswith('/admin'):
            return self.get_response(request)

        # Если включен режим техработ
        if getattr(settings, 'MAINTENANCE_MODE', False):
            return render(request, 'cms/maintenance.html', status=503)

        return self.get_response(request)