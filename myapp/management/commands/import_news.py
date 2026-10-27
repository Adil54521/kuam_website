import json
import re

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from myapp.models import News


INPUT_FILE = "prepared_news.json"


def normalize_category(category_slug):
    """
    Убирает языковой суффикс.
    """

    category_slug = (
        category_slug
        .strip()
        .lower()
    )

    for suffix in (
        "-rus",
        "-kaz",
        "-eng",
    ):

        if category_slug.endswith(
            suffix
        ):

            return category_slug[
                :-len(suffix)
            ]

    return category_slug


class Command(BaseCommand):

    help = (
        "Импорт новостей "
        "из prepared_news.json"
    )

    def handle(
        self,
        *args,
        **kwargs
    ):

        # =====================================================
        # LOAD JSON
        # =====================================================

        try:

            with open(
                INPUT_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

        except FileNotFoundError:

            self.stdout.write(
                self.style.ERROR(
                    f"Файл не найден: {INPUT_FILE}"
                )
            )

            return

        except json.JSONDecodeError as error:

            self.stdout.write(
                self.style.ERROR(
                    f"Ошибка JSON: {error}"
                )
            )

            return

        if not isinstance(
            data,
            list
        ):

            self.stdout.write(
                self.style.ERROR(
                    "Корень JSON должен быть массивом."
                )
            )

            return

        created = 0
        updated = 0
        skipped = 0

        # =====================================================
        # IMPORT
        # =====================================================

        for item in data:

            # -------------------------------------------------
            # TITLE
            # -------------------------------------------------

            title = item.get(
                "title",
                ""
            )

            title = title.strip()

            title = re.sub(
                r"\s+",
                " ",
                title
            )

            if not title:

                self.stdout.write(
                    self.style.WARNING(
                        "Пропущена новость без заголовка"
                    )
                )

                skipped += 1
                continue

            # -------------------------------------------------
            # CATEGORY
            # -------------------------------------------------

            original_category = item.get(
                "category_slug",
                "news"
            )

            original_category = (
                original_category.strip()
            )

            category_slug = (
                normalize_category(
                    original_category
                )
            )

            category_title = (
                normalize_category(
                    item.get(
                        "category_title",
                        category_slug
                    )
                )
            )

            # -------------------------------------------------
            # BASE SLUG
            # -------------------------------------------------

            base_slug = slugify(
                title
            )

            if not base_slug:

                base_slug = "news"

            news_slug = (
                f"{category_slug}-{base_slug}"
            )

            # -------------------------------------------------
            # Ищем существующую новость
            # -------------------------------------------------

            news = News.objects.filter(
                slug=news_slug
            ).first()

            # -------------------------------------------------
            # Если slug занят другой новостью
            # -------------------------------------------------

            if news is None:

                # Сначала пытаемся найти
                # по категории + title
                news = (
                    News.objects.filter(
                        category_slug=category_slug,
                        title=title
                    )
                    .first()
                )

            # -------------------------------------------------
            # UPDATE
            # -------------------------------------------------

            if news:

                news.category_slug = (
                    category_slug
                )

                news.category_title = (
                    category_title
                )

                news.title = title

                news.slug = news_slug

                news.content_rus = (
                    item.get(
                        "content_rus"
                    )
                )

                news.content_kaz = (
                    item.get(
                        "content_kaz"
                    )
                )

                news.content_eng = (
                    item.get(
                        "content_eng"
                    )
                )

                news.is_active = True

                news.save()

                updated += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"ОБНОВЛЕНО: {news_slug}"
                    )
                )

                continue

            # -------------------------------------------------
            # CREATE
            # -------------------------------------------------

            News.objects.create(
                category_slug=category_slug,

                category_title=category_title,

                title=title,

                slug=news_slug,

                content_rus=item.get(
                    "content_rus"
                ),

                content_kaz=item.get(
                    "content_kaz"
                ),

                content_eng=item.get(
                    "content_eng"
                ),

                is_active=True,
            )

            created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"СОЗДАНО: {news_slug}"
                )
            )

        # =====================================================
        # RESULT
        # =====================================================

        self.stdout.write("")
        self.stdout.write(
            "=" * 80
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Создано: {created}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Обновлено: {updated}"
            )
        )

        if skipped:

            self.stdout.write(
                self.style.WARNING(
                    f"Пропущено: {skipped}"
                )
            )

        self.stdout.write(
            "=" * 80
        )