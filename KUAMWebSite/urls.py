from django.contrib import admin
from django.urls import path, include
from myapp import views
from django.conf import settings
from django.conf.urls.static import static
import uuid
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
from myapp.views import get_news, news_last_page

urlpatterns = [
    path('page/new/<str:identification>/', views.block_modal, name='block_modal'),  # Сначала свои маршруты
    path('admin/imagetext/', views.show_imagetext, name='imagetext'),
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home_page'),
    path('news/', views.news_list, name='news_list'),
    path('news/item/<slug:slug>/', views.news_item_detail, name='news_item_detail'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('news/<slug>/last/', news_last_page,name='news_last_page'),
    path('news/<slug:slug>/<int:page>/', views.news_list, name='news_list_paginated'),
    path('sdg/', views.sdg_page, name='sdg_page'),
    path('head/', views.head, name='head'),
    path('merop/', views.meropriatia, name='meropriatia'),
    path('bakalavr/', views.bakalavr, name='bakalavr'),
    path('office-commerse/', views.office, name='office'),
    path('learning-science/', views.learning, name='learning'),
    path('science-research/', views.research, name='research'),
    path('science-projects/', views.projects, name='projects'),
    path('portfolio-scientiest/', views.portfolio, name='portfolio'),
    path('organigramma/', views.organigramma, name='organigramma'),
    path('science-department/', views.science_department, name='science_department'),
    path('accreditation/', views.accreditation, name='accreditation'),
    path('polozhenia/', views.polozhenia, name='polozhenia'),
    path('academicpartners/', views.academicpartners, name='academicpartners'),
    path('candidates/', views.candidates, name='candidates'),
    #path('yarmarka/', views.yarmarka, name='yarmarka'),
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
    path("api/get-page/", views.get_page_content, name="get_page_content"),
    path('upload/', views.ckeditor5_upload, name='ckeditor5_upload'),
    path('editor/', views.editor_view, name='editor'),
    path("api/news/", get_news, name="get_news"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'myapp.views.error'
