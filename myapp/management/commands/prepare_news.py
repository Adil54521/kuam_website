import json
import re
from difflib import SequenceMatcher

from django.core.management.base import BaseCommand


INPUT_FILE = "news_export.json"
OUTPUT_FILE = "prepared_news.json"
MATCH_THRESHOLD = 40

# =========================================================
# РАЗРЕШЁННЫЕ КАТЕГОРИИ
# =========================================================

CATEGORY_LANGUAGES = {
    # Обычные новости
    "news-rus": "rus",
    "news-kaz": "kaz",
    "news-eng": "eng",

    # Международный отдел
    "news-international-rus": "rus",
    "news-international-kaz": "kaz",
    "news-international-eng": "eng",

    # Новости главной страницы
    "news-main-rus": "rus",
    "news-main-kaz": "kaz",
    "news-main-en": "eng",
}


# =========================================================
# ГРУППЫ КАТЕГОРИЙ
# =========================================================

CATEGORY_GROUPS = [
    {
        "name": "NEWS",
        "rus": "news-rus",
        "kaz": "news-kaz",
        "eng": "news-eng",
    },
    {
        "name": "NEWS INTERNATIONAL",
        "rus": "news-international-rus",
        "kaz": "news-international-kaz",
        "eng": "news-international-eng",
    },
    {
        "name": "NEWS MAIN",
        "rus": "news-main-rus",
        "kaz": "news-main-kaz",
        "eng": "news-main-en",
    },
]


# =========================================================
# ТРАНСЛИТ
# =========================================================

TRANSLIT_MAP = str.maketrans({
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "h",
    "ц": "c",
    "ч": "ch",
    "ш": "sh",
    "щ": "sch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",

    "қ": "q",
    "ғ": "g",
    "ң": "n",
    "ұ": "u",
    "ү": "u",
    "һ": "h",
    "і": "i",
    "ә": "a",
    "ө": "o",
})


class Command(BaseCommand):

    # =========================================================
    # LANGUAGE
    # =========================================================

    def get_language(self, category_slug):
        category_slug = category_slug.strip().lower()
        return CATEGORY_LANGUAGES.get(category_slug)

    # =========================================================
    # CATEGORY
    # =========================================================

    def is_allowed_category(self, category_slug):
        category_slug = category_slug.strip().lower()
        return category_slug in CATEGORY_LANGUAGES

    # =========================================================
    # HTML -> TEXT
    # =========================================================

    def html_to_text(self, html):
        if not html:
            return ""

        text = re.sub(
            r"<[^>]+>",
            " ",
            html
        )

        replacements = {
            "&nbsp;": " ",
            "&amp;": "&",
            "&quot;": '"',
            "&lt;": "<",
            "&gt;": ">",
            "&#39;": "'",
            "&#x27;": "'",
            "&ndash;": "-",
            "&mdash;": "-",
            "&laquo;": '"',
            "&raquo;": '"',
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =========================================================
    # TITLE
    # =========================================================

    def extract_title(self, content):
        """
        Ищет наиболее подходящий заголовок.

        Приоритет:
        h2 -> h3 -> h1 -> первая содержательная строка
        """

        if not content:
            return ""

        # Сначала h2
        match = re.search(
            r"<h2\b[^>]*>(.*?)</h2\s*>",
            content,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:
            title = self.html_to_text(match.group(1))

            if title:
                return title

        # Потом h3
        match = re.search(
            r"<h3\b[^>]*>(.*?)</h3\s*>",
            content,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:
            title = self.html_to_text(match.group(1))

            if title:
                return title

        # Потом h1
        match = re.search(
            r"<h1\b[^>]*>(.*?)</h1\s*>",
            content,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:
            title = self.html_to_text(match.group(1))

            if title:
                return title

        # Если заголовка нет - берём первый текстовый абзац
        text = self.html_to_text(content)

        return text[:200].strip()

    # =========================================================
    # НОРМАЛИЗАЦИЯ
    # =========================================================

    def normalize_text(self, text):
        text = self.html_to_text(text)

        text = text.lower()

        text = text.translate(TRANSLIT_MAP)

        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =========================================================
    # TOKENS
    # =========================================================

    def extract_tokens(self, content):
        text = self.normalize_text(content)

        tokens = set()

        for token in text.split():

            if len(token) >= 3:
                tokens.add(token)

        return tokens

    # =========================================================
    # NUMBERS
    # =========================================================
    def extract_numbers(self, content):
        text = self.html_to_text(content)

        return set(
            re.findall(
                r"\d+",
                text
            )
        )
    def extract_dates(self, content):
        """
        Извлекает даты формата:
        07/09/2026
        07.09.2026
        07-09-2026
        """

        if not content:
            return set()

        text = self.html_to_text(content)

        dates = re.findall(
            r"\b\d{2}[./-]\d{2}[./-]\d{4}\b",
            text
        )

        normalized = set()

        for date in dates:
            normalized.add(
                re.sub(r"[./-]", ".", date)
            )

        return normalized

    def extract_images(self, content):
        """
        Извлекает src изображений из HTML.
        """

        if not content:
            return set()

        images = re.findall(
            r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']',
            content,
            flags=re.IGNORECASE
        )

        normalized = set()

        for image in images:
            image = image.strip().lower()

            # Берём имя файла
            filename = image.split("/")[-1]

            if filename:
                normalized.add(filename)

        return normalized
    # =========================================================
    # URL
    # =========================================================

    def extract_urls(self, content):
        if not content:
            return set()

        urls = re.findall(
            r'https?://[^\s"<]+',
            content,
            flags=re.IGNORECASE
        )

        normalized = set()

        for url in urls:

            url = url.rstrip(
                '.,);]'
            )

            normalized.add(
                url.lower()
            )

        return normalized

    # =========================================================
    # SIGNATURE
    # =========================================================

    def get_signature(self, content):
        return {
            "tokens": self.extract_tokens(content),
            "numbers": self.extract_numbers(content),
            "urls": self.extract_urls(content),
            "dates": self.extract_dates(content),
            "images": self.extract_images(content),
        }

    # =========================================================
    # MATCH SCORE
    # =========================================================

    def calculate_match_score(
        self,
        first_content,
        second_content
    ):
        first = self.get_signature(first_content)
        second = self.get_signature(second_content)

        score = 0

        # =====================================================
        # ДАТЫ
        # =====================================================

        common_dates = (
            first["dates"]
            & second["dates"]
        )

        # Если у обеих новостей есть даты,
        # но даты разные — это почти наверняка
        # разные новости.
        if (
            first["dates"]
            and second["dates"]
            and not common_dates
        ):
            return -1000

        if common_dates:
            score += 100

        # =====================================================
        # ИЗОБРАЖЕНИЯ
        # =====================================================

        common_images = (
            first["images"]
            & second["images"]
        )

        if common_images:
            score += min(
                len(common_images) * 40,
                120
            )

        # =====================================================
        # URL
        # =====================================================

        common_urls = (
            first["urls"]
            & second["urls"]
        )

        if common_urls:
            score += min(
                len(common_urls) * 100,
                200
            )

        # =====================================================
        # NUMBERS
        # =====================================================

        common_numbers = (
            first["numbers"]
            & second["numbers"]
        )

        # Цифры теперь дают намного меньше веса,
        # чтобы 07, 15 и т.п. не склеивали разные новости.

        score += min(
            len(common_numbers) * 2,
            10
        )

        # =====================================================
        # TOKENS
        # =====================================================

        common_tokens = (
            first["tokens"]
            & second["tokens"]
        )

        score += min(
            len(common_tokens) * 3,
            30
        )

        # =====================================================
        # TOKEN SIMILARITY
        # =====================================================

        if (
            first["tokens"]
            and second["tokens"]
        ):

            first_text = " ".join(
                sorted(first["tokens"])
            )

            second_text = " ".join(
                sorted(second["tokens"])
            )

            ratio = SequenceMatcher(
                None,
                first_text,
                second_text
            ).ratio()

            score += int(
                ratio * 20
            )

        return score

    # =========================================================
    # SPLIT CONTENT
    # =========================================================

    def split_content_into_news(self, content):
        """
        Главный способ разделения:

            <hr>

        Каждый блок между <hr> считается отдельной новостью.

        Если <hr> нет, используется h2/h3/h1.
        """

        if not content:
            return []

        content = content.strip()

        if not content:
            return []

        # -----------------------------------------------------
        # 1. Разделяем по HR
        # -----------------------------------------------------

        parts = re.split(
            r"<hr\b[^>]*>",
            content,
            flags=re.IGNORECASE
        )

        cleaned_parts = []

        for part in parts:

            part = part.strip()

            if not part:
                continue

            # Удаляем полностью пустые блоки
            text = self.html_to_text(part)

            if not text:
                continue

            cleaned_parts.append(
                part
            )

        # Если реально получили несколько блоков,
        # считаем их отдельными новостями
        if len(cleaned_parts) > 1:

            result = []

            for part in cleaned_parts:

                result.append(
                    {
                        "title": self.extract_title(part),
                        "content": part,
                    }
                )

            return result

        # -----------------------------------------------------
        # 2. Fallback: H1/H2/H3
        # -----------------------------------------------------

        matches = list(
            re.finditer(
                r"<h[1-3]\b[^>]*>",
                content,
                flags=re.IGNORECASE
            )
        )

        if not matches:

            return [
                {
                    "title": self.extract_title(content),
                    "content": content,
                }
            ]

        result = []

        for index, match in enumerate(matches):

            start = match.start()

            if index + 1 < len(matches):
                end = matches[
                    index + 1
                ].start()
            else:
                end = len(content)

            news_content = content[
                start:end
            ].strip()

            if not news_content:
                continue

            result.append(
                {
                    "title": self.extract_title(
                        news_content
                    ),
                    "content": news_content,
                }
            )

        return result

    # =========================================================
    # BUILD CATEGORIES
    # =========================================================

    def build_categories(self, data):

        categories = {
            category_slug: {
                "rus": [],
                "kaz": [],
                "eng": [],
            }
            for category_slug
            in CATEGORY_LANGUAGES
        }

        for item in data:

            category_slug = (
                item.get(
                    "category_slug",
                    ""
                )
                .strip()
                .lower()
            )

            if not category_slug:
                self.stdout.write(
                    self.style.WARNING(
                        "У записи отсутствует category_slug"
                    )
                )

                continue

            if not self.is_allowed_category(
                category_slug
            ):
                self.stdout.write(
                    self.style.WARNING(
                        f"ПРОПУСК: неизвестная категория "
                        f"'{category_slug}'"
                    )
                )

                continue

            language = self.get_language(
                category_slug
            )

            if language is None:
                continue

            content = item.get(
                "content",
                ""
            )

            news_items = (
                self.split_content_into_news(
                    content
                )
            )

            self.stdout.write(
                f"{category_slug}: "
                f"language={language}, "
                f"новостей={len(news_items)}"
            )

            categories[
                category_slug
            ][language].extend(
                news_items
            )

        return categories

    # =========================================================
    # MATCH NEWS
    # =========================================================

    def match_news(
        self,
        master_news,
        translation_news,
        language
    ):
        """
        Ищет перевод для каждой новости.

        Сначала проверяется дата.
        Затем используются изображения, URL и текстовый score.

        Кандидат с отрицательным score никогда не используется.
        """

        matched = []

        available = set(
            range(len(translation_news))
        )

        for master_index, master in enumerate(
            master_news
        ):

            best_index = None
            best_score = -100000

            master_dates = self.extract_dates(
                master["content"]
            )

            for candidate_index in available:

                candidate = translation_news[
                    candidate_index
                ]

                candidate_dates = self.extract_dates(
                    candidate["content"]
                )

                # =================================================
                # ЖЁСТКАЯ ПРОВЕРКА ДАТЫ
                # =================================================

                if (
                    master_dates
                    and candidate_dates
                    and not (
                        master_dates
                        & candidate_dates
                    )
                ):
                    continue

                score = self.calculate_match_score(
                    master["content"],
                    candidate["content"]
                )

                if score > best_score:
                    best_score = score
                    best_index = candidate_index

            # =====================================================
            # НЕ НАШЛИ
            # =====================================================

            if (
                best_index is None
                or best_score < MATCH_THRESHOLD
            ):

                matched.append(None)

                self.stdout.write(
                    self.style.WARNING(
                        f"[{language}] "
                        f"ПЕРЕВОД НЕ НАЙДЕН: "
                        f"{master['title']} "
                        f"(score={best_score})"
                    )
                )

                continue

            # =====================================================
            # НАШЛИ
            # =====================================================

            translation = translation_news[
                best_index
            ]

            matched.append(
                {
                    "item": translation,
                    "score": best_score,
                }
            )

            available.remove(
                best_index
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"[{language}] "
                    f"score={best_score} | "
                    f"{master['title']} "
                    f"-> "
                    f"{translation['title']}"
                )
            )

        return matched

    # =========================================================
    # PREPARE CATEGORY
    # =========================================================

    def prepare_translated_category(
        self,
        group_name,
        category_slugs,
        category_data
    ):

        rus_news = category_data.get(
            "rus",
            []
        )

        kaz_news = category_data.get(
            "kaz",
            []
        )

        eng_news = category_data.get(
            "eng",
            []
        )

        self.stdout.write("")
        self.stdout.write(
            "=" * 100
        )

        self.stdout.write(
            f"ГРУППА: {group_name}"
        )

        self.stdout.write(
            f"RUS: {len(rus_news)}"
        )

        self.stdout.write(
            f"KAZ: {len(kaz_news)}"
        )

        self.stdout.write(
            f"ENG: {len(eng_news)}"
        )

        self.stdout.write(
            "=" * 100
        )

        # -----------------------------------------------------
        # Русский является основной версией,
        # если он существует.
        # -----------------------------------------------------

        if rus_news:

            master_news = rus_news

            kaz_matches = self.match_news(
                master_news,
                kaz_news,
                "KAZ"
            )

            eng_matches = self.match_news(
                master_news,
                eng_news,
                "ENG"
            )

        # -----------------------------------------------------
        # Если русского нет, используем казахский
        # -----------------------------------------------------

        elif kaz_news:

            master_news = kaz_news

            rus_matches = self.match_news(
                master_news,
                rus_news,
                "RUS"
            )

            eng_matches = self.match_news(
                master_news,
                eng_news,
                "ENG"
            )

            kaz_matches = [
                {
                    "item": item,
                    "score": 999,
                }
                for item in master_news
            ]

        # -----------------------------------------------------
        # Если есть только английский
        # -----------------------------------------------------

        else:

            master_news = eng_news

            rus_matches = self.match_news(
                master_news,
                rus_news,
                "RUS"
            )

            kaz_matches = self.match_news(
                master_news,
                kaz_news,
                "KAZ"
            )

            eng_matches = [
                {
                    "item": item,
                    "score": 999,
                }
                for item in master_news
            ]

        result = []

        # -----------------------------------------------------
        # Создание готовых объектов
        # -----------------------------------------------------

        for index, master in enumerate(
            master_news
        ):

            if rus_news:

                rus_item = master

                kaz_match = kaz_matches[
                    index
                ]

                eng_match = eng_matches[
                    index
                ]

            elif kaz_news:

                kaz_item = master

                rus_match = rus_matches[
                    index
                ]

                eng_match = eng_matches[
                    index
                ]

                rus_item = (
                    rus_match["item"]
                    if rus_match
                    else None
                )

                kaz_item = kaz_item

            else:

                eng_item = master

                rus_match = rus_matches[
                    index
                ]

                kaz_match = kaz_matches[
                    index
                ]

                rus_item = (
                    rus_match["item"]
                    if rus_match
                    else None
                )

                kaz_item = (
                    kaz_match["item"]
                    if kaz_match
                    else None
                )

                eng_item = eng_item

            # -------------------------------------------------
            # Если русский главный
            # -------------------------------------------------

            if rus_news:

                kaz_item = (
                    kaz_match["item"]
                    if kaz_match
                    else None
                )

                eng_item = (
                    eng_match["item"]
                    if eng_match
                    else None
                )

            # -------------------------------------------------
            # Заголовок
            # -------------------------------------------------

            if rus_item and rus_item.get("title"):
                title = rus_item["title"]

            elif kaz_item and kaz_item.get("title"):
                title = kaz_item["title"]

            elif eng_item and eng_item.get("title"):
                title = eng_item["title"]

            else:
                title = (
                    f"Новость {index + 1}"
                )

            # -------------------------------------------------
            # Основной category_slug
            # -------------------------------------------------

            category_slug = (
                category_slugs.get("rus")
                or category_slugs.get("kaz")
                or category_slugs.get("eng")
            )

            result.append(
                {
                    "category_slug": category_slug,

                    "category_title": category_slug,

                    "title": title,

                    "content_rus": (
                        rus_item["content"]
                        if rus_item
                        else ""
                    ),

                    "content_kaz": (
                        kaz_item["content"]
                        if kaz_item
                        else ""
                    ),

                    "content_eng": (
                        eng_item["content"]
                        if eng_item
                        else ""
                    ),
                }
            )

        return result

    # =========================================================
    # HANDLE
    # =========================================================

    def handle(
        self,
        *args,
        **options
    ):

        self.stdout.write("")
        self.stdout.write(
            f"Загрузка: {INPUT_FILE}"
        )

        # -----------------------------------------------------
        # JSON
        # -----------------------------------------------------

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

        self.stdout.write(
            f"Исходных JSON-записей: "
            f"{len(data)}"
        )

        # -----------------------------------------------------
        # Категории
        # -----------------------------------------------------

        categories = (
            self.build_categories(
                data
            )
        )

        prepared_news = []

        # -----------------------------------------------------
        # Каждая группа
        # -----------------------------------------------------

        for group in CATEGORY_GROUPS:

            result = (
                self.prepare_translated_category(
                    group_name=group["name"],

                    category_slugs={
                        "rus": group["rus"],
                        "kaz": group["kaz"],
                        "eng": group["eng"],
                    },

                    category_data={
                        "rus": categories[
                            group["rus"]
                        ]["rus"],

                        "kaz": categories[
                            group["kaz"]
                        ]["kaz"],

                        "eng": categories[
                            group["eng"]
                        ]["eng"],
                    }
                )
            )

            prepared_news.extend(
                result
            )

        # -----------------------------------------------------
        # Сохранение
        # -----------------------------------------------------

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                prepared_news,
                file,
                ensure_ascii=False,
                indent=2
            )

        # -----------------------------------------------------
        # Итог
        # -----------------------------------------------------

        self.stdout.write("")
        self.stdout.write(
            "=" * 100
        )

        self.stdout.write(
            self.style.SUCCESS(
                "ГОТОВО"
            )
        )

        self.stdout.write(
            f"Подготовлено новостей: "
            f"{len(prepared_news)}"
        )

        self.stdout.write(
            f"Файл: {OUTPUT_FILE}"
        )

        self.stdout.write(
            "=" * 100
        )

        self.stdout.write("")
        self.stdout.write(
            "Категории:"
        )

        for category in sorted(
            {
                item["category_slug"]
                for item in prepared_news
            }
        ):

            self.stdout.write(
                f"  - {category}"
            )