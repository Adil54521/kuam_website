from django.shortcuts import render, get_object_or_404, redirect
from .models import Block, Page, MenuItem, Head, Bakalavriat, OfficeCommerse, Footer, Main, News, NewsImage
from django.contrib import messages
from django.db.models import Prefetch
from django.http import FileResponse, Http404, HttpResponseRedirect, JsonResponse
from django.contrib.staticfiles import finders
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import uuid
from django.core.files.storage import default_storage
from django.utils.html import strip_tags
from django.utils.text import get_valid_filename
from django.utils.translation import get_language
from django.urls import reverse
import os
from django.core.paginator import Paginator
from django.template.loader import render_to_string
import re
from html import unescape
from myapp.models import HeadHunterModel
from datetime import datetime, timezone as datetime_timezone
from .forms import SDGContactForm
from .sdg_rules import SDG_RULES, attach_sdg_tags, get_sdg_goals


SDG_NEWS_CANDIDATE_LIMIT = 80
SDG_NEWS_DISPLAY_LIMIT = 6


def _stylesheet_response(static_path):
    """Serve the two project stylesheets when Nginx static mapping is unavailable."""
    resolved_path = finders.find(static_path)
    if not resolved_path:
        raise Http404("Stylesheet not found")

    response = FileResponse(
        open(resolved_path, "rb"),
        content_type="text/css; charset=utf-8",
    )
    response["Cache-Control"] = "public, max-age=3600"
    return response


def sdg_stylesheet(request):
    return _stylesheet_response("myapp/css/sdg.css")


def news_stylesheet(request):
    return _stylesheet_response("myapp/css/news.css")


def sdg_news_detail_stylesheet(request):
    return _stylesheet_response("myapp/css/sdg_news_detail.css")


def _parse_sdg_goal(raw_goal):
    try:
        goal_number = int(raw_goal)
    except (TypeError, ValueError):
        return None
    return goal_number if goal_number in SDG_RULES else None


def _localized_news_content(news_object, language_code):
    language = (language_code or "ru").split("-")[0]
    field_by_language = {
        "ru": "content_rus",
        "kk": "content_kaz",
        "en": "content_eng",
    }
    primary_field = field_by_language.get(language, "content_rus")
    ordered_fields = (primary_field, "content_rus", "content_kaz", "content_eng")

    for field_name in dict.fromkeys(ordered_fields):
        content = getattr(news_object, field_name, "") or ""
        if content:
            return content
    return ""


def _prepare_news_for_display(
    news_object,
    language_code,
    *,
    remove_duplicate_heading=False,
):
    attach_sdg_tags(news_object)
    content = _localized_news_content(news_object, language_code)
    heading_match = re.search(
        r"<h[1-3]\b[^>]*>(.*?)</h[1-3]\s*>",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    extracted_heading = (
        " ".join(unescape(strip_tags(heading_match.group(1))).split())
        if heading_match
        else ""
    )
    news_object.display_title = (news_object.title or "").strip() or extracted_heading or "Новость"

    if remove_duplicate_heading:
        # A dedicated detail page already renders display_title above the rich
        # text. Remove only an exactly matching leading heading there. The
        # paginated news list deliberately keeps the CMS heading because it is
        # the only visible title after removing the old detail-page link.
        leading_heading_match = re.match(
            r"^\s*<h(?P<level>[1-3])\b[^>]*>(?P<text>.*?)</h(?P=level)\s*>",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if leading_heading_match:
            leading_heading_text = " ".join(
                unescape(strip_tags(leading_heading_match.group("text"))).split()
            )
            if leading_heading_text.casefold() == news_object.display_title.casefold():
                content = content[leading_heading_match.end():].lstrip()

    news_object.display_content = content

    content_with_tag_separators = re.sub(r"<[^>]+>", " ", content)
    plain_text = " ".join(unescape(strip_tags(content_with_tag_separators)).split())
    if plain_text.casefold().startswith(news_object.display_title.casefold()):
        plain_text = plain_text[len(news_object.display_title):].lstrip(" .—–-:")
    news_object.display_excerpt = (
        f"{plain_text[:220].rstrip()}…" if len(plain_text) > 220 else plain_text
    )

    images = list(news_object.images.all()) if hasattr(news_object, "images") else []
    news_object.preview_image = images[0] if images else None
    news_object.preview_image_url = (
        news_object.preview_image.image.url
        if news_object.preview_image and news_object.preview_image.image
        else ""
    )
    if not news_object.preview_image_url:
        embedded_image_match = re.search(
            r"<img\b[^>]*\bsrc\s*=\s*(['\"])(?P<src>.*?)\1",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if embedded_image_match:
            news_object.preview_image_url = embedded_image_match.group("src")
    return news_object


def _get_sdg_news(selected_goal_number, language_code):
    candidates = (
        News.objects.filter(is_active=True)
        .prefetch_related(
            Prefetch("images", queryset=NewsImage.objects.order_by("order", "id"))
        )
        .order_by("-created_at")[:SDG_NEWS_CANDIDATE_LIMIT]
    )

    related_news = []
    for news_object in candidates:
        _prepare_news_for_display(news_object, language_code)
        tag_numbers = {tag["number"] for tag in news_object.sdg_tags}
        if not tag_numbers:
            continue
        if selected_goal_number is not None and selected_goal_number not in tag_numbers:
            continue

        related_news.append(news_object)
        if len(related_news) == SDG_NEWS_DISPLAY_LIMIT:
            break

    return related_news


def _get_sdg_logo_url():
    main_item = Main.objects.filter(is_active=True).order_by("-id").first()
    if not main_item or not main_item.image_logo:
        return None
    if not default_storage.exists(main_item.image_logo.name):
        return None
    return main_item.image_logo.url


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

    new_news = News.objects.filter(
        is_active=True,
        created_at__gte=datetime(2026, 9, 10, tzinfo=datetime_timezone.utc),
    ).order_by('created_at')

    new_news = [{'type': 'new', 'data': item,} for item in new_news]
    
    all_news = old_news + new_news

    paginator = Paginator(all_news, 1)
    
    #cur_classifier()
    
    page_obj = paginator.get_page(page)
    language_code = getattr(request, "LANGUAGE_CODE", None) or get_language() or "ru"

    # Classify only the new news objects present on the requested page. The
    # result is a temporary presentation attribute and is not stored in DB.
    for news_item in page_obj.object_list:
        if news_item.get("type") != "new":
            continue

        _prepare_news_for_display(news_item["data"], language_code)
    
    return render(request, 'cms/news_list.html', {'page_obj': page_obj, 'slug': slug,})


def sdg_page(request):
    """Render the SDG directory, related news and project-office contact form."""
    selected_goal_number = _parse_sdg_goal(request.GET.get("goal"))
    sdg_goals = get_sdg_goals()
    selected_goal = next(
        (goal for goal in sdg_goals if goal["number"] == selected_goal_number),
        None,
    )

    if request.method == "POST":
        form = SDGContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Спасибо! Ваше сообщение отправлено проектному офису ЦУР.")
            redirect_url = reverse("sdg_page")
            if selected_goal_number is not None:
                redirect_url = f"{redirect_url}?goal={selected_goal_number}"
            return HttpResponseRedirect(f"{redirect_url}#contacts")
    else:
        form = SDGContactForm()

    language_code = getattr(request, "LANGUAGE_CODE", None) or get_language() or "ru"
    return render(
        request,
        "cms/sdg.html",
        {
            "sdg_goals": sdg_goals,
            "selected_goal": selected_goal,
            "related_news": _get_sdg_news(selected_goal_number, language_code),
            "contact_form": form,
            "sdg_logo_url": _get_sdg_logo_url(),
        },
    )


def news_item_detail(request, slug):
    news_queryset = News.objects.filter(is_active=True).prefetch_related("images")
    news_object = news_queryset.filter(slug=slug).first()
    if news_object is None and str(slug).isdigit():
        news_object = news_queryset.filter(pk=int(slug)).first()
    if news_object is None:
        raise Http404("News item not found")

    language_code = getattr(request, "LANGUAGE_CODE", None) or get_language() or "ru"
    _prepare_news_for_display(
        news_object,
        language_code,
        remove_duplicate_heading=True,
    )
    return render(
        request,
        "cms/news_item_detail.html",
        {
            "news": news_object,
            "sdg_tags": news_object.sdg_tags,
        },
    )
    
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
    new_news = News.objects.filter(
        is_active=True,
        created_at__gte=datetime(2026, 9, 10, tzinfo=datetime_timezone.utc),
    ).order_by('created_at')

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
