from datetime import datetime, timezone as datetime_timezone

from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from .models import News, Page, SDGContactMessage


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
        self.assertEqual(
            reverse("news_item_detail", kwargs={"slug": self.education_news.slug}),
            "/news/item/education-sdg-news/",
        )

    def test_page_without_goal_shows_tagged_news(self):
        response = self.client.get(reverse("sdg_page"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cms/sdg.html")
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
        self.assertContains(response, f'{reverse("sdg_page")}?goal=4#goals')

    def test_news_list_links_to_sdg_and_real_news_detail(self):
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
        self.assertContains(response, f'{reverse("sdg_page")}?goal=4#goals')
        self.assertContains(
            response,
            reverse("news_item_detail", kwargs={"slug": self.education_news.slug}),
        )

    def test_static_assets_are_discoverable(self):
        for path in (
            "myapp/css/news.css",
            "myapp/css/sdg.css",
            "myapp/js/sdg.js",
        ):
            with self.subTest(path=path):
                self.assertIsNotNone(finders.find(path))

    def test_contact_form_contains_csrf_token(self):
        response = self.client.get(reverse("sdg_page"))
        self.assertContains(response, "csrfmiddlewaretoken")
