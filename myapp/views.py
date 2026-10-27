from django.shortcuts import render, get_object_or_404, redirect
from .models import Block, Page, MenuItem, Head, Bakalavriat, OfficeCommerse, Footer, News
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import uuid
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
from django.urls import reverse
import os
from django.core.paginator import Paginator
from django.template.loader import render_to_string
import re
from myapp.models import HeadHunterModel
from datetime import datetime
def block_modal(request, identification):
    block = get_object_or_404(Block, identification=identification)

    return render(request, 'cms/new_construct.html', {'block': block})
    
def show_imagetext(request):
    # Можно передать контекст, если нужно
    context = {
        'title': 'Пример отображения HTML',
    }
    return render(request, 'admin/imagetext.html', context)
    
# Вьюха для главной страницы
def home_page(request):
    return render(request, 'cms/kuam.html')

def error(request, exception):
    return render(request, "cms/404.html", status=404)
    
def news_list(request, slug, page=1):
    news_item = get_object_or_404(Page, slug=slug)
    old_news = news_item.get_news_items()

    old_news = [{'type': 'old','data': item,} for item in old_news]

    new_news = News.objects.filter(is_active=True, created_at__gte=datetime(2026, 9, 10, 0, 0, 0)).order_by('created_at')

    new_news = [{'type': 'new', 'data': item,} for item in new_news]
    
    all_news = old_news + new_news

    paginator = Paginator(all_news, 1)
    
    #cur_classifier()
    
    page_obj = paginator.get_page(page)
    
    return render(request, 'cms/news_list.html', {'page_obj': page_obj, 'slug': slug,})
    
def news_detail(request, slug):
    # Ищем страницу по slug
    page = get_object_or_404(Page, slug=slug)

    # Находим новость по slug в списке news_slugs
    if slug in page.news_slugs:
        # Получаем индекс новости
        news_index = page.news_slugs.index(slug)
        # Разделяем контент на новости
        news_items = page.get_news_items()
        news_content = news_items[news_index]
        return render(request, 'cms/news_detail.html', {'news_content': news_content})
    else:
        # Если slug не найден в news_slugs, выводим 404 или редирект
        return redirect('news_list')

# Страница с конкретным содержимым
def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)  # Получаем страницу по slug

    block_content = ""  # по умолчанию пусто
    bl_identifications = Block.objects.values_list('identification', flat=True)
    
    # Ищем блок, который совпадает с слагом страницы
    for block_ident in bl_identifications:
        if block_ident == page.slug:
            block = Block.objects.get(identification=block_ident)
            block_content = render_to_string('cms/block_template.html', {'block': block})
            # Вставляем блок в контент страницы
            page_content = re.sub(
                r'<!--\s*\{\{\s*block_content_placeholder\s*\}\}\s*-->(.*?)<!--\s*\{\{\s*block_content_end\s*\}\}\s*-->',
                f'<!-- {{ block_content_placeholder }} -->{block_content}<!-- {{ block_content_end }} -->',
                page.content,
                flags=re.DOTALL
            )
            break
    else:
        # Если совпадений нет, просто выводим исходный контент страницы
        page_content = page.content

    return render(request, 'cms/page_detail.html', {'page': page, 'page_content': page_content})

#def cur_classifier(request):
   #try:
      #api_key = os.getenv("GEMINI_API_KEY")
      #base_url = "https://generativelanguage.googleapis.com/v1beta"
      #model = "models/gemini-3.8-flash"
       
      #url = (f"{base_url}/cachedContents")
         
      #headers = {"Content-Type": "application/json", "x-goog-api-key": self.api_key,}
        
        

def head(request):
    return render(request, 'cms/head.html')
    
def bakalavr(request):
    return render(request, 'cms/bakalavr.html')
    
def meropriatia(request):
    return render(request, 'cms/merop.html')

def learning(request):
    return render(request, 'cms/learning-science.html')
    
def office(request):
    return render(request, 'cms/office-commerse.html')

def research(request):
    return render(request, 'cms/science-research.html')

def organigramma(request):
    return render(request, 'cms/organigramma.html')

def projects(request):
    return render(request, 'cms/science-projects.html')

def portfolio(request):
    return render(request, 'cms/portfolio_scientiest.html')

def science_department(request):
    return render(request, 'cms/science-department.html')

def accreditation(request):
    return render(request, 'cms/accreditation.html')

def polozhenia(request):
    return render(request, 'cms/polozhenia.html')

def candidates(request):
    return render(request, 'cms/candidates.html')

def academicpartners(request):
    return render(request, 'cms/academicpartners.html')
    
def editor_view(request):
    return render(request, 'cms/editor.html')

def yarmarka(request):
    return render(request, 'cms/yarmarka.html')

@csrf_exempt
def ckeditor5_upload(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        upload = request.FILES['upload']
        filename = get_valid_filename(upload.name)
        
        # Убедитесь, что директория существует, если нет — создайте её
        full_path = os.path.join(filename)
        
        # Уникализация имени файла, если такой файл уже существует
        if default_storage.exists(full_path):
            base, ext = os.path.splitext(filename)
            i = 1
            while default_storage.exists(f'{publications_path}{base}_{i}{ext}'):
                i += 1
            full_path = f'{publications_path}{base}_{i}{ext}'

        try:
            # Сохраняем файл
            default_storage.save(full_path, upload)
            file_url = default_storage.url(full_path)

            # Логируем для проверки
            print("Saved file:", full_path, "URL:", file_url)

            return JsonResponse({'url': file_url})
        except Exception as e:
            print("Upload error:", e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Нет файла для загрузки'}, status=400)

def get_page_content(request):
    slug = request.GET.get("slug")
    try:
        page = Page.objects.get(slug=slug)
        return JsonResponse({
            "title": page.title,
            "content": page.content
        })
    except Page.DoesNotExist:
        return JsonResponse({"error": "Page not found"}, status=404)

def get_news(request):

    lang = request.GET.get("lang", "ru")

    content_fields = {"ru": "content_rus", "kk": "content_kaz", "en": "content_eng",}

    content_field = content_fields.get(lang, "content_kaz")

    news_queryset = (News.objects.filter(category_slug="news-main",is_active=True).prefetch_related("images").order_by("-created_at"))

    result = []

    for news in news_queryset:

        content = getattr(news, content_field, "") or ""

        title = news.title

        match = re.search(
            r"<h2\b[^>]*>(.*?)</h2\s*>",
            content,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:
            title = re.sub(
                r"<[^>]+>",
                "",
                match.group(1)
            ).strip()

        images = []

        for image in news.images.all().order_by("order"):
            if image.image:
                images.append(
                    image.image.url
                )

        result.append({
            "id": news.id,
            "title": title,
            "slug": news.slug,
            "content": content,
            "images": images,
            "image": images[0] if images else None,
        })

    return JsonResponse({
        "news": result
    })
    
def news_last_page(request, slug):
    news_item = get_object_or_404(Page, slug=slug)

    # Старая логика
    old_news = news_item.get_news_items()

    # Новые News с 10 сентября 2026 и далее
    new_news = News.objects.filter(is_active=True, created_at__gte=datetime(2026, 9, 10, 0, 0, 0)).order_by('created_at')

    # Объединяем
    all_news = list(old_news) + list(new_news)

    # Пагинация
    paginator = Paginator(all_news, 1)

    # Редирект на последнюю страницу
    return redirect(
        'news_list_paginated',
        slug=slug,
        page=paginator.num_pages
    )