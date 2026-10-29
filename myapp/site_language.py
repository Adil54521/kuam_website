"""Shared language selection for the legacy frontend and Django views."""

import re
from urllib.parse import urlencode

from django.conf import settings
from django.urls import reverse
from django.utils import formats, timezone, translation


SUPPORTED_LANGUAGES = ("kk", "ru", "en")
LANGUAGE_ALIASES = {
    "kk": "kk",
    "kaz": "kk",
    "kz": "kk",
    "ru": "ru",
    "rus": "ru",
    "en": "en",
    "eng": "en",
}
LANGUAGE_SESSION_KEY = "site_language"
LANGUAGE_COOKIE_NAME = getattr(settings, "LANGUAGE_COOKIE_NAME", "django_language")


def normalize_language(value, default=None):
    normalized = LANGUAGE_ALIASES.get(str(value or "").lower())
    if normalized:
        return normalized
    if default is not None:
        return normalize_language(default, "ru")
    return normalize_language(settings.LANGUAGE_CODE, "ru")


def _language_from_news_slug(request):
    resolver_match = getattr(request, "resolver_match", None)
    slug = (resolver_match.kwargs.get("slug", "") if resolver_match else "") or ""
    match = re.search(r"(?:^|-)(kaz|kz|kk|rus|ru|eng|en)(?:-|$)", slug.lower())
    return normalize_language(match.group(1)) if match else None


def get_active_language(request):
    """Return kk/ru/en using the site's route, session and Django cookie."""
    slug_language = _language_from_news_slug(request)
    candidates = (
        slug_language,
        request.GET.get("lang"),
        request.session.get(LANGUAGE_SESSION_KEY),
        request.COOKIES.get(LANGUAGE_COOKIE_NAME),
        getattr(request, "LANGUAGE_CODE", None),
        settings.LANGUAGE_CODE,
    )
    language = next(
        (normalize_language(value) for value in candidates if value),
        normalize_language(settings.LANGUAGE_CODE),
    )
    request.LANGUAGE_CODE = language
    if slug_language:
        request.session[LANGUAGE_SESSION_KEY] = language
    translation.activate(language)
    return language


def language_switch_url(request, language, anchor=""):
    query = {
        "lang": normalize_language(language),
        "next": request.get_full_path(),
    }
    if anchor:
        query["anchor"] = anchor.lstrip("#")
    return f"{reverse('set_site_language')}?{urlencode(query)}"


def format_localized_datetime(value, language, *, short=False):
    if not value:
        return ""
    try:
        value = timezone.localtime(value)
    except (ValueError, TypeError):
        pass
    format_name = "DATE_FORMAT" if short else "DATETIME_FORMAT"
    with translation.override(normalize_language(language)):
        return formats.date_format(value, format_name, use_l10n=True)

