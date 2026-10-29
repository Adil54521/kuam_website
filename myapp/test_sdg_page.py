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
            content_kaz=(
                "<h2>Білім күні және жаңа білім беру бағдарламалары</h2>"
                "<p>Сапалы білім туралы материал.</p>"
            ),
            content_eng=(
                "<h2>Knowledge Day and new educational programmes</h2>"
                "<p>A story about quality education.</p>"
            ),
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
        self.assertEqual(reverse("set_site_language"), "/language/set/")
        self.assertEqual(reverse("sdg_stylesheet"), "/assets/css/sdg.css")
        self.assertEqual(reverse("news_stylesheet"), "/assets/css/news.css")
        self.assertEqual(reverse("sdg_script"), "/assets/js/sdg.js")
        self.assertEqual(
            reverse("sdg_news_detail_stylesheet"),
            "/assets/css/sdg-news-detail.css",
        )
        self.assertEqual(
            reverse("news_item_detail", kwargs={"slug": self.education_news.slug}),
            "/news/item/education-sdg-news/",
        )

    def use_language(self, language):
        self.client.cookies["django_language"] = language

    def test_language_endpoint_syncs_session_cookie_and_main_site(self):
        response = self.client.get(
            reverse("set_site_language"),
            {
                "lang": "kaz",
                "next": f'{reverse("sdg_page")}?goal=16',
                "anchor": "news",
            },
        )

        self.assertRedirects(
            response,
            f'{reverse("sdg_page")}?goal=16#news',
            fetch_redirect_response=False,
        )
        self.assertEqual(self.client.session["site_language"], "kk")
        self.assertEqual(response.cookies["django_language"].value, "kk")

        home_response = self.client.get(reverse("home_page"))
        self.assertContains(home_response, 'data-active-language="kk"')
        sdg_response = self.client.get(reverse("sdg_page"), {"goal": "16"})
        self.assertEqual(sdg_response.context["active_language"], "kk")
        self.assertContains(sdg_response, "ТДМ 16")

    def test_sdg_language_switcher_preserves_goal_and_news_anchor(self):
        response = self.client.get(reverse("sdg_page"), {"goal": "16"})

        self.assertContains(
            response,
            "/language/set/?lang=kk&amp;next=/sdg/%3Fgoal%3D16&amp;anchor=news",
        )
        self.assertContains(response, "data-language-link", count=3)

    def test_sdg_page_is_fully_localized_in_kazakh(self):
        self.use_language("kk")
        response = self.client.get(reverse("sdg_page"), {"goal": "4"})

        self.assertEqual(response.context["active_language"], "kk")
        self.assertContains(response, '<html lang="kk">')
        self.assertContains(response, "Тұрақты дамудың 17 мақсаты")
        self.assertContains(response, "Сапалы білім")
        self.assertContains(response, "ТДМ 4")
        self.assertContains(response, "Хабарлама жіберу")
        self.assertNotContains(response, "Вклад КУАМ")

    def test_sdg_page_is_fully_localized_in_english(self):
        self.use_language("en")
        response = self.client.get(reverse("sdg_page"), {"goal": "16"})

        self.assertEqual(response.context["active_language"], "en")
        self.assertContains(response, '<html lang="en">')
        self.assertContains(response, "17 Sustainable Development Goals")
        self.assertContains(response, "Peace, Justice and Strong Institutions")
        self.assertContains(response, "SDG 16")
        self.assertContains(response, "Send message")

    def test_news_detail_uses_russian_content_and_labels(self):
        self.use_language("ru")
        response = self.client.get(
            reverse("news_item_detail", kwargs={"slug": self.education_news.slug})
        )

        self.assertContains(response, "Материал о качественном образовании.")
        self.assertContains(response, "ЦУР 4")
        self.assertContains(response, "Качественное образование")
        self.assertFalse(response.context["news"].is_translation_fallback)

    def test_news_detail_uses_kazakh_content_title_and_sdg_name(self):
        self.use_language("kk")
        response = self.client.get(
            reverse("news_item_detail", kwargs={"slug": self.education_news.slug})
        )

        self.assertContains(response, "Білім күні және жаңа білім беру бағдарламалары")
        self.assertContains(response, "Сапалы білім туралы материал.")
        self.assertContains(response, "ТДМ 4")
        self.assertContains(response, "Сапалы білім")
        self.assertFalse(response.context["news"].is_translation_fallback)

    def test_news_detail_uses_english_content_title_and_sdg_name(self):
        self.use_language("en")
        response = self.client.get(
            reverse("news_item_detail", kwargs={"slug": self.education_news.slug})
        )

        self.assertContains(response, "Knowledge Day and new educational programmes")
        self.assertContains(response, "A story about quality education.")
        self.assertContains(response, "SDG 4")
        self.assertContains(response, "Quality Education")
        self.assertFalse(response.context["news"].is_translation_fallback)

    def test_missing_translation_falls_back_and_shows_localized_notice(self):
        self.use_language("kk")
        response = self.client.get(
            reverse("news_item_detail", kwargs={"slug": self.partnership_news.slug})
        )

        self.assertTrue(response.context["news"].is_translation_fallback)
        self.assertEqual(response.context["news"].display_language, "ru")
        self.assertContains(
            response,
            "Бұл жаңалықтың аудармасы әзірге қолжетімсіз.",
        )
        self.assertContains(response, "ТДМ 17")
        self.assertContains(response, "Тұрақты даму мақсатындағы әріптестік")

    def test_fallback_order_uses_kazakh_when_english_and_russian_are_empty(self):
        kazakh_only = News.objects.create(
            category_slug="news-main",
            title="",
            slug="kazakh-only-news",
            content_kaz="<h2>Қазақ тіліндегі жаңалық</h2><p>Қолжетімді мәтін.</p>",
        )
        self.use_language("en")

        response = self.client.get(
            reverse("news_item_detail", kwargs={"slug": kazakh_only.slug})
        )

        self.assertEqual(response.context["news"].display_language, "kk")
        self.assertTrue(response.context["news"].is_translation_fallback)
        self.assertContains(response, "Қазақ тіліндегі жаңалық")
        self.assertContains(
            response,
            "This news item is not yet available in the selected language.",
        )

    def test_news_dates_are_localized(self):
        dates = {}
        for language in ("ru", "kk", "en"):
            self.use_language(language)
            response = self.client.get(
                reverse(
                    "news_item_detail",
                    kwargs={"slug": self.education_news.slug},
                )
            )
            dates[language] = response.context["news"].display_date

        self.assertEqual(len(set(dates.values())), 3)
        for formatted_date in dates.values():
            self.assertIn("2026", formatted_date)

    def test_neutral_detail_shows_localized_not_assigned_state(self):
        self.use_language("en")
        response = self.client.get(
            reverse("news_item_detail", kwargs={"slug": self.neutral_news.slug})
        )

        self.assertContains(response, "Not assigned to an SDG")
        self.assertContains(response, "View all SDGs")
        self.assertContains(response, f'{reverse("sdg_page")}#goals')

    def test_english_invalid_form_keeps_values_and_localizes_errors(self):
        self.use_language("en")
        response = self.client.post(
            reverse("sdg_page"),
            {
                "name": "Alice Example",
                "email": "not-an-email",
                "subject": "Partnership idea",
                "message": "short",
            },
        )

        self.assertContains(response, 'value="Alice Example"')
        self.assertContains(response, 'value="Partnership idea"')
        self.assertContains(response, "Enter a valid email address.")
        self.assertContains(response, "The message must contain at least 10 characters.")
        self.assertContains(response, "Consent to data processing is required.")

    def test_regular_page_does_not_load_sdg_or_news_styles(self):
        for language in ("kk", "ru", "en"):
            with self.subTest(language=language):
                self.use_language(language)
                response = self.client.get(reverse("home_page"))

                self.assertEqual(response.status_code, 200)
                self.assertContains(
                    response,
                    f'data-active-language="{language}"',
                )
                self.assertNotContains(response, "/assets/css/sdg.css")
                self.assertNotContains(response, "/assets/css/news.css")
                self.assertNotContains(response, "/assets/css/sdg-news-detail.css")

    def test_news_list_uses_kazakh_content_labels_and_goal_names(self):
        page = Page.objects.create(
            title="Жаңалықтар",
            slug="localized-news-page",
            content="<h2>Мұрағат</h2>",
        )
        News.objects.filter(pk=self.education_news.pk).update(
            created_at=datetime(2026, 10, 20, tzinfo=datetime_timezone.utc)
        )
        self.use_language("kk")

        response = self.client.get(
            reverse(
                "news_list_paginated",
                kwargs={"slug": page.slug, "page": 2},
            )
        )

        self.assertContains(response, "Білім күні және жаңа білім беру бағдарламалары")
        self.assertContains(response, "Сапалы білім туралы материал.")
        self.assertContains(response, "ТДМ-ға қосқан үлесі:")
        self.assertContains(response, "ТДМ 4")
        self.assertContains(response, "Сапалы білім")
        self.assertNotContains(response, "Материал о качественном образовании.")

    def test_news_slug_language_alias_overrides_default_language(self):
        Page.objects.create(
            title="Жаңалықтар",
            slug="news-main-kaz",
            content="<h2>Мұрағат жаңалығы</h2>",
        )

        response = self.client.get(
            reverse(
                "news_list_paginated",
                kwargs={"slug": "news-main-kaz", "page": 1},
            )
        )

        self.assertEqual(response.context["active_language"], "kk")
        self.assertContains(response, "Жаңалықтар")
        home_response = self.client.get(reverse("home_page"))
        self.assertContains(home_response, 'data-active-language="kk"')

    def test_page_without_goal_shows_tagged_news(self):
        response = self.client.get(reverse("sdg_page"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cms/sdg.html")
        self.assertContains(
            response,
            '/assets/css/sdg.css?v=20261029-1',
        )
        self.assertContains(response, 'class="sdg-page"')
        self.assertContains(response, 'data-active-language="ru"')
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
        self.assertContains(response, "Сообщение успешно отправлено.")
        message = SDGContactMessage.objects.get()
        self.assertEqual(message.email, "user@example.com")
        self.assertTrue(message.consent)

    def test_contact_success_message_follows_active_language(self):
        expected_messages = {
            "kk": "Хабарлама сәтті жіберілді.",
            "en": "Your message has been sent successfully.",
        }
        for index, (language, expected) in enumerate(expected_messages.items()):
            with self.subTest(language=language):
                self.use_language(language)
                response = self.client.post(
                    reverse("sdg_page"),
                    {
                        "name": "Test User",
                        "email": f"user{index}@example.com",
                        "subject": "SDG initiative",
                        "message": "A sufficiently detailed project message.",
                        "consent": "on",
                    },
                    follow=True,
                )
                self.assertContains(response, expected)

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
            '/assets/css/sdg-news-detail.css?v=20261029-1',
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
            '/assets/css/news.css?v=20261029-2',
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

    def test_news_list_shows_localized_empty_sdg_state_without_detail_link(self):
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
        self.assertContains(response, 'class="news-sdg-empty"')
        self.assertContains(response, "Не относится к ЦУР")
        self.assertContains(response, f'{reverse("sdg_page")}#goals')
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

    def test_sdg_script_fallback_endpoint_returns_javascript(self):
        response = self.client.get(reverse("sdg_script"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response["Content-Type"].startswith("application/javascript")
        )
        self.assertIn(b"data-language-link", b"".join(response.streaming_content))

    def test_contact_form_contains_csrf_token(self):
        response = self.client.get(reverse("sdg_page"))
        self.assertContains(response, "csrfmiddlewaretoken")
