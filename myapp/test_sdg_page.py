from datetime import datetime, timezone as datetime_timezone
from html.parser import HTMLParser

from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from .models import News, Page, SDGContactMessage


class NestedAnchorDetector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchor_depth = 0
        self.has_nested_anchor = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            if self.anchor_depth:
                self.has_nested_anchor = True
            self.anchor_depth += 1

    def handle_endtag(self, tag):
        if tag == "a" and self.anchor_depth:
            self.anchor_depth -= 1


class SDGPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.education_news = News.objects.create(
            category_slug="news-main",
            title="День знаний и новые образовательные программы",
            slug="education-sdg-news",
            content_rus=(
                "<h2>День знаний и новые образовательные программы</h2>"
                "<p>Материал о качественном образовании.</p>"
            ),
            content_kaz="<p>Сапалы білім туралы материал.</p>",
            content_eng="<p>A story about quality education.</p>",
        )
        cls.partnership_news = News.objects.create(
            category_slug="news-main",
            title="Меморандум международного сотрудничества",
            slug="partnership-sdg-news",
            content_rus="<h2>Международное сотрудничество</h2><p>Подписан меморандум.</p>",
        )
        cls.neutral_news = News.objects.create(
            category_slug="news-main",
            title="Плановая встреча кафедры",
            slug="neutral-news",
            content_rus="<p>Участники обсудили рабочие вопросы и календарный план.</p>",
        )

    def test_named_urls(self):
        self.assertEqual(reverse("sdg_page"), "/sdg/")
        self.assertEqual(reverse("sdg_stylesheet"), "/assets/css/sdg.css")
        self.assertEqual(reverse("news_stylesheet"), "/assets/css/news.css")
        self.assertEqual(
            reverse("sdg_news_detail_stylesheet"),
            "/assets/css/sdg-news-detail.css",
        )
        self.assertEqual(
            reverse("news_item_detail", kwargs={"slug": self.education_news.slug}),
            "/news/item/education-sdg-news/",
        )

    def test_page_without_goal_shows_tagged_news(self):
        response = self.client.get(reverse("sdg_page"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cms/sdg.html")
        self.assertContains(
            response,
            '/assets/css/sdg.css?v=20261028-6',
        )
        self.assertContains(response, '<body class="sdg-page">')
        self.assertIsNone(response.context["selected_goal"])
        self.assertContains(response, self.education_news.title)
        self.assertContains(response, self.partnership_news.title)
        self.assertNotContains(response, self.neutral_news.title)

    def test_valid_goal_filters_news(self):
        response = self.client.get(reverse("sdg_page"), {"goal": "4"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_goal"]["number"], 4)
        self.assertContains(response, self.education_news.title)
        self.assertNotContains(response, self.partnership_news.title)

    def test_goal_17_is_accepted(self):
        response = self.client.get(reverse("sdg_page"), {"goal": "17"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_goal"]["number"], 17)
        self.assertContains(response, self.partnership_news.title)

    def test_invalid_goal_values_are_ignored(self):
        for value in ("abc", "0", "18"):
            with self.subTest(value=value):
                response = self.client.get(reverse("sdg_page"), {"goal": value})
                self.assertEqual(response.status_code, 200)
                self.assertIsNone(response.context["selected_goal"])

    def test_valid_contact_form_is_saved_and_redirected(self):
        response = self.client.post(
            f"{reverse('sdg_page')}?goal=4",
            {
                "name": "Тестовый пользователь",
                "email": "user@example.com",
                "subject": "Инициатива",
                "message": "Предлагаю обсудить новый университетский проект.",
                "consent": "on",
            },
            follow=True,
        )

        self.assertEqual(
            response.redirect_chain,
            [(f"{reverse('sdg_page')}?goal=4#contacts", 302)],
        )
        self.assertContains(response, "Спасибо! Ваше сообщение отправлено")
        message = SDGContactMessage.objects.get()
        self.assertEqual(message.email, "user@example.com")
        self.assertTrue(message.consent)

    def test_contact_form_rejects_missing_consent_and_short_message(self):
        response = self.client.post(
            reverse("sdg_page"),
            {
                "name": "Пользователь",
                "email": "user@example.com",
                "subject": "Вопрос",
                "message": "Коротко",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(SDGContactMessage.objects.exists())
        self.assertIn("consent", response.context["contact_form"].errors)
        self.assertIn("message", response.context["contact_form"].errors)

    def test_news_detail_contains_sdg_link(self):
        response = self.client.get(
            reverse("news_item_detail", kwargs={"slug": self.education_news.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cms/news_item_detail.html")
        self.assertContains(response, f'{reverse("sdg_page")}?goal=4#news')
        self.assertContains(
            response,
            '/assets/css/sdg-news-detail.css?v=20261028-1',
        )
        self.assertEqual(response.context["sdg_tags"], response.context["news"].sdg_tags)
        self.assertNotContains(response, "← К новостям ЦУР")
        self.assertEqual(
            response.content.decode("utf-8").count(self.education_news.title),
            1,
        )

    def test_news_detail_accepts_numeric_primary_key_fallback(self):
        response = self.client.get(
            reverse(
                "news_item_detail",
                kwargs={"slug": str(self.education_news.pk)},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["news"].pk, self.education_news.pk)

    def test_sdg_news_cards_use_separate_main_and_goal_links(self):
        response = self.client.get(reverse("sdg_page"))
        html = response.content.decode("utf-8")
        parser = NestedAnchorDetector()
        parser.feed(html)

        self.assertContains(response, 'class="sdg-news-card"')
        self.assertContains(response, 'class="sdg-news-card__main"')
        self.assertContains(response, 'class="sdg-news-card__goals"')
        self.assertContains(
            response,
            reverse(
                "news_item_detail",
                kwargs={"slug": self.education_news.slug},
            ),
        )
        self.assertContains(response, f'{reverse("sdg_page")}?goal=4#news')
        self.assertFalse(parser.has_nested_anchor)

    def test_news_list_replaces_detail_title_link_with_sdg_tags(self):
        page = Page.objects.create(
            title="Новости",
            slug="test-news-page",
            content="<h2>Старая новость</h2><p>Архивный текст.</p>",
        )
        News.objects.filter(pk=self.education_news.pk).update(
            created_at=datetime(2026, 10, 20, tzinfo=datetime_timezone.utc)
        )

        response = self.client.get(
            reverse(
                "news_list_paginated",
                kwargs={"slug": page.slug, "page": 2},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'{reverse("sdg_page")}?goal=4#news')
        self.assertContains(
            response,
            '/assets/css/news.css?v=20261029-1',
        )
        self.assertContains(response, 'class="news-sdg-tags"')
        self.assertContains(response, 'class="news-sdg-tags__item"')
        self.assertContains(response, 'class="news-page news-list-page"')
        self.assertNotContains(
            response,
            reverse(
                "news_item_detail",
                kwargs={"slug": self.education_news.slug},
            ),
        )
        self.assertContains(
            response,
            f"<h2>{self.education_news.title}</h2>",
            html=True,
        )

    def test_news_list_omits_empty_sdg_container_and_detail_title_link(self):
        Page.objects.create(
            title="Новости без тегов",
            slug="neutral-news-page",
            content="",
        )
        News.objects.exclude(pk=self.neutral_news.pk).update(is_active=False)
        News.objects.filter(pk=self.neutral_news.pk).update(
            created_at=datetime(2026, 10, 20, tzinfo=datetime_timezone.utc)
        )

        response = self.client.get(
            reverse(
                "news_list_paginated",
                kwargs={"slug": "neutral-news-page", "page": 1},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'class="news-sdg-tags"')
        self.assertNotContains(
            response,
            reverse(
                "news_item_detail",
                kwargs={"slug": self.neutral_news.slug},
            ),
        )
        self.assertContains(
            response,
            "Участники обсудили рабочие вопросы и календарный план.",
        )

    def test_static_assets_are_discoverable(self):
        for path in (
            "myapp/css/news.css",
            "myapp/css/sdg.css",
            "myapp/css/sdg_news_detail.css",
            "myapp/js/sdg.js",
        ):
            with self.subTest(path=path):
                self.assertIsNotNone(finders.find(path))

    def test_stylesheet_fallback_endpoints_return_css(self):
        for url_name, marker in (
            ("sdg_stylesheet", b".sdg-page"),
            ("news_stylesheet", b".news-page"),
            ("sdg_news_detail_stylesheet", b".sdg-news-detail"),
        ):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response["Content-Type"].startswith("text/css"))
                self.assertIn(marker, b"".join(response.streaming_content))

    def test_contact_form_contains_csrf_token(self):
        response = self.client.get(reverse("sdg_page"))
        self.assertContains(response, "csrfmiddlewaretoken")
