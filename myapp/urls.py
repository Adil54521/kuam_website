from django.urls import path
from .views import custom_page, page_view

urlpatterns = [
    path('kupi-admin', admin.sit),
]