import json
from django.core.management.base import BaseCommand
from myapp.models import Page


class Command(BaseCommand):
    help = "Экспорт новостей из Page.content в JSON"

    def handle(self, *args, **kwargs):
        result = []

        pages = Page.objects.filter(
            slug__startswith="news-"
        ).order_by("id")

        for page in pages:
            news_parts = page.get_news_items()

            for part in news_parts:
                if not part.strip():
                    continue

                # Берём заголовок новости из <h2> или <h1>
                title = ""

                if "<h2>" in part:
                    title = part.split("</h2>")[0]
                    title = title.replace("<h2>", "", 1).strip()

                elif "<h1>" in part:
                    title = part.split("</h1>")[0]
                    title = title.replace("<h1>", "", 1).strip()

                result.append({
                    "category_slug": page.slug,
                    "category_title": page.title,
                    "title": title,
                    "content": part,
                })

        with open(
            "news_export.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                result,
                f,
                ensure_ascii=False,
                indent=2
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Экспортировано новостей: {len(result)}"
            )
        )

