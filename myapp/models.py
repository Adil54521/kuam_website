from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
import os
from django import forms


class Block(models.Model):
    identification = models.SlugField(blank=True, unique=False)
    image = models.ImageField(upload_to="uploads/", blank=True, null=True)
    video_url = models.FileField(upload_to="uploads/", blank=True, null=True)
    def delete(self, *args, **kwargs):
        # удаляем изображение, если есть
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        # удаляем видео, если есть
        if self.video_url and os.path.isfile(self.video_url.path):
            os.remove(self.video_url.path)
        # вызываем стандартное удаление записи
        super().delete(*args, **kwargs)

class BlockText(models.Model):
    block = models.ForeignKey(Block, related_name="texts", on_delete=models.CASCADE)
    text_ru = models.TextField(blank=True, null=True)
    text_en = models.TextField(blank=True, null=True)
    text_kz = models.TextField(blank=True, null=True)
    second_text_kk = RichTextField("Абзац (қаз)", blank=True, null=True)
    second_text_ru = RichTextField("Абзац (рус)", blank=True, null=True)
    second_text_en = RichTextField("Абзац (англ)", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        ordering = ["order"]

class BlockFile(models.Model):
    block = models.ForeignKey(Block, related_name="files", on_delete=models.CASCADE)
    text_ru = models.TextField(blank=True, null=True)
    text_en = models.TextField(blank=True, null=True)
    text_kz = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="uploads/docs/")
    title = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

class Page(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField(config_name='default', null=True)
    slug = models.SlugField(unique=True, blank=True)

    def get_news_items(self):
        news_parts = self.content.split('<h2>')
        news_parts = [part for part in news_parts if part.strip()]
        news_parts.reverse()
        return news_parts

    def generate_news_slugs(self):
        news_parts = self.get_news_items()
        slugs = []
        for i, part in enumerate(news_parts):
            title = part.split('</h2>')[0]  # Берем текст внутри тега <h2>
            slug = slugify(title)
            # Если slug уже существует, добавляем индекс, чтобы он был уникальным
            if slug in slugs:
                slug = f"{slug}-{i + 1}"
            slugs.append(slug)
        return slugs

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title_kk = models.CharField("Название (қаз)", max_length=200)
    title_ru = models.CharField("Название (рус)", max_length=200)
    title_en = models.CharField("Название (eng)", max_length=200)

    url = models.CharField("Ссылка", max_length=300, blank=True)

    parent = models.ForeignKey(
        'self',
        verbose_name="Родительский пункт меню",
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE
    )

    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    css_class = models.CharField(
        "CSS класс (no-dropdown, menu-toggle и т.п.)",
        max_length=100,
        blank=True
    )

    def title(self, lang="ru"):
        return getattr(self, f"title_{lang}", self.title_ru)

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Меню"
        ordering = ["order"]

    def __str__(self):
        return self.title_ru


class Head(models.Model):
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    title_kk = models.CharField("Фио (қаз)", max_length=200)
    title_ru = models.CharField("Фио (рус)", max_length=200)
    title_en = models.CharField("Фио (eng)", max_length=200)
    description_kk = RichTextField("Абзац (қаз)", blank=True, null=True)
    description_ru = RichTextField("Абзац (рус)", blank=True, null=True)
    description_en = RichTextField("Абзац (англ)", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)
    css_class = models.CharField("CSS класс (container)", max_length=100, blank=True)

    class Meta:
        verbose_name = "Пункт Руководство университета"
        verbose_name_plural = "Руководство университета"
        ordering = ["order"]

    def __str__(self):
        return self.title_ru


class Bakalavriat(models.Model):
    title_kk_title = models.CharField("Заголовок(қаз)", max_length=200, blank=True, null=True)
    title_ru_title = models.CharField("Заголовок(рус)", max_length=200, blank=True, null=True)
    title_en_title = models.CharField("Заголовок(англ)", max_length=200, blank=True, null=True)
    url = models.CharField("Ссылка", max_length=300, blank=True)
    title_kk = models.CharField("Название курса (қаз)", max_length=200)
    title_ru = models.CharField("Название курса (рус)", max_length=200)
    title_en = models.CharField("Название курса (eng)", max_length=200)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Пункт Бакалавриат"
        verbose_name_plural = "Бакалавриат"
        ordering = ["order"]

    def __str__(self):
        return self.title_ru


class Meropriatia(models.Model):
    title_ru = models.CharField("Название мероприятия (рус)", max_length=200, blank=True, null=True)
    title_kk = models.CharField("Название мероприятия (каз)", max_length=200, blank=True, null=True)
    title_en = models.CharField("Название мероприятия (англ)", max_length=200, blank=True, null=True)
    summary_ru = RichTextField("Содержание (рус)", max_length=100000)
    summary_kk = RichTextField("Содержание (каз)", max_length=100000)
    summary_en = RichTextField("Содержание (англ)", max_length=100000)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)
    css_class = models.CharField("CSS класс (container, dropdown)", max_length=100, blank=True)

    class Meta:
        verbose_name = "Пункт Мероприятия (путь /merop/)"
        verbose_name_plural = "Мероприятия"
        ordering = ["order"]

    def __str__(self):
        return self.title_ru


class OfficeCommerse(models.Model):
    title_ru = models.CharField("Заголовок (рус)", max_length=200, blank=True, null=True)
    title_kk = models.CharField("Заголовок (каз)", max_length=200, blank=True, null=True)
    title_en = models.CharField("Заголовок (англ)", max_length=200, blank=True, null=True)
    summary_ru = models.CharField("Содержание(рус)", max_length=200, blank=True, null=True)
    summary_kk = models.CharField("Содержание(каз)", max_length=200, blank=True, null=True)
    summary_en = models.CharField("Содержание(англ)", max_length=200, blank=True, null=True)
    url = models.CharField("Ссылка", max_length=300, blank=True)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Пункт Издательская детельность (путь /office-commerse/)"
        verbose_name_plural = "Издательская детельность"
        ordering = ["order"]

class Learning(models.Model):
    title_ru = models.CharField("Заголовок (рус)", max_length=200, blank=True, null=True)
    title_kk = models.CharField("Заголовок (каз)", max_length=200, blank=True, null=True)
    title_en = models.CharField("Заголовок (англ)", max_length=200, blank=True, null=True)
    summary_title_ru = models.CharField("Заголовок выпадающего списка (рус)", max_length=200, blank=True, null=True)
    summary_title_kk = models.CharField("Заголовок выпадающего списка (каз)", max_length=200, blank=True, null=True)
    summary_title_en = models.CharField("Заголовок выпадающего списка (англ)", max_length=200, blank=True,null=True)
    summary_ru = RichTextField("Содержание (рус)", max_length=100000, default='')
    summary_kk = RichTextField("Содержание (каз)", max_length=100000, default='')
    summary_en = RichTextField("Содержание (англ)", max_length=100000, default='')
    url = models.CharField("Ссылка", max_length=300, blank=True, null=True)
    css_class = models.CharField("CSS класс (container, dropdown)", max_length=100, blank=True, null=True)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Пункт Коворкинг-центр (путь /learning-science/)"
        verbose_name_plural = "Коворкинг-центр"
        ordering = ["order"]

class LearningCarousel(models.Model):
    carousel_img = models.ForeignKey(Learning, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Пункт Карусель Коворкинг-центра"
        verbose_name_plural = "Карусель Коворкинг-центра"
        ordering = ["order"]

class Research(models.Model):
    title_ru = models.CharField("Заголовок (рус)", max_length=200, blank=True, null=True)
    title_kk = models.CharField("Заголовок (каз)", max_length=200, blank=True, null=True)
    title_en = models.CharField("Заголовок (англ)", max_length=200, blank=True, null=True)
    title_summary_ru = models.CharField("Заголовок с ссылкой (рус)", max_length=200, blank=True, null=True)
    title_summary_kk = models.CharField("Заголовок с ссылкой (каз)", max_length=200, blank=True, null=True)
    title_summary_en = models.CharField("Заголовок с ссылкой (англ)", max_length=200, blank=True, null=True)
    url = models.CharField("Ссылка", max_length=300, blank=True, null=True)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Пункт Научно-исследовательская деятельность ППС (путь - /science-research/)"
        verbose_name_plural = "Научно-исследовательская деятельность ППС"
        ordering = ["order"]

class ResearchModal(models.Model):
    parent = models.ForeignKey(
        "self",
        related_name="children",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Родительская модалка"
    )
    title_modal_ru = models.CharField("Заголовок (рус)", max_length=200, blank=True, null=True)
    title_modal_kk = models.CharField("Заголовок (каз)", max_length=200, blank=True, null=True)
    title_modal_en = models.CharField("Заголовок (англ)", max_length=200, blank=True, null=True)
    title_within_modal_ru = models.CharField("Заголовок внутри модалки (рус)", max_length=200, blank=True, null=True)
    title_within_modal_kk = models.CharField("Заголовок внутри модалки (каз)", max_length=200, blank=True, null=True)
    title_within_modal_en = models.CharField("Заголовок внутри модалки (англ)", max_length=200, blank=True, null=True)
    title_url_modal_ru = models.CharField("Заголовок с ссылкой (рус)", max_length=200, blank=True, null=True)
    title_url_modal_kk = models.CharField("Заголовок с ссылкой (каз)", max_length=200, blank=True, null=True)
    title_url_modal_en = models.CharField("Заголовок с ссылкой (англ)", max_length=200, blank=True, null=True)
    url = models.CharField("Ссылка", max_length=300, blank=True, null=True)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Модалка Научно-исследовательская деятельность ППС (путь - /science-research/)"
        verbose_name_plural = "Модалка научно-исследовательской деятельности"
        ordering = ["order"]

class Organigramma(models.Model):
    url = models.CharField("Ссылка", max_length=100, blank=True, null=True)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Органиграмма (путь - /organigramma/)"
        verbose_name_plural = "Органиграмма"
        ordering = ["order"]

class Projects(models.Model):
    title_ru = models.CharField("Заголовок (рус)", max_length=200, blank=True, null=True)
    title_kk = models.CharField("Заголовок (каз)", max_length=200, blank=True, null=True)
    title_en = models.CharField("Заголовок (англ)", max_length=200, blank=True, null=True)
    title_summary_ru = models.CharField("Заголовок с ссылкой (рус)", max_length=200, blank=True, null=True)
    title_summary_kk = models.CharField("Заголовок с ссылкой (каз)", max_length=200, blank=True, null=True)
    title_summary_en = models.CharField("Заголовок с ссылкой (англ)", max_length=200, blank=True, null=True)
    url = models.CharField("Ссылка", max_length=300, blank=True, null=True)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Пункт научно-координационные центры (путь - /science-projects/)"
        verbose_name_plural = "Научно-координационные центры"
        ordering = ["order"]

class ProjectsModal(models.Model):
    parent = models.ForeignKey("self", related_name="children", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Родительская модалка")
    title_modal_ru = models.CharField("Заголовок (рус)", max_length=200, blank=True, null=True)
    title_modal_kk = models.CharField("Заголовок (каз)", max_length=200, blank=True, null=True)
    title_modal_en = models.CharField("Заголовок (англ)", max_length=200, blank=True, null=True)
    title_within_modal_ru = models.CharField("Заголовок внутри модалки (рус)", max_length=200, blank=True, null=True)
    title_within_modal_kk = models.CharField("Заголовок внутри модалки (каз)", max_length=200, blank=True, null=True)
    title_within_modal_en = models.CharField("Заголовок внутри модалки (англ)", max_length=200, blank=True, null=True)
    title_url_modal_ru = models.CharField("Заголовок с ссылкой (рус)", max_length=200, blank=True, null=True)
    title_url_modal_kk = models.CharField("Заголовок с ссылкой (каз)", max_length=200, blank=True, null=True)
    title_url_modal_en = models.CharField("Заголовок с ссылкой (англ)", max_length=200, blank=True, null=True)
    url = models.CharField("Ссылка", max_length=300, blank=True, null=True)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Модалка научно-координационные центры (путь - /science-projects/)"
        verbose_name_plural = "Модалка научно-координационные центры"
        ordering = ["order"]

class PortfolioCategory(models.Model):
    title_ru = models.CharField("Заголовок (рус)", max_length=200)
    title_kk = models.CharField("Заголовок (каз)", max_length=200, blank=True)
    title_en = models.CharField("Заголовок (англ)", max_length=200, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Заголовки портфолио ученых"
        verbose_name_plural = "Заголовки портфолио ученых"
        ordering = ["order"]

    def __str__(self):
        return self.title_ru

class Portfolio (models.Model):
    category = models.ForeignKey(PortfolioCategory, on_delete=models.CASCADE, null=True, blank=True)
    name_ru = models.CharField("ФИО (рус)", max_length=200, blank=True, null=True)
    name_kk = models.CharField("ФИО (қаз)", max_length=200, blank=True, null=True)
    name_en = models.CharField("ФИО (англ)", max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    summary_ru = RichTextField("Содержание (рус)", max_length=100000, blank=True, null=True)
    summary_kk = RichTextField("Содержание (каз)", max_length=100000, blank=True, null=True)
    summary_en = RichTextField("Содержание (англ)", max_length=100000, blank=True, null=True)
    url_email = models.CharField("Ссылка на почту", max_length=300, blank=True, null=True)
    url_email_text_ru = models.CharField("Название почты (рус)", max_length=300, blank=True, null=True)
    url_email_text_kk = models.CharField("Название почты (каз)", max_length=300, blank=True, null=True)
    icon = models.ImageField(verbose_name="Иконка", upload_to='uploads/', blank=True, null=True)
    url_email_text_en = models.CharField("Название почты (англ)", max_length=300, blank=True, null=True)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Портфолио (путь - /portfolio-scientiest/)"
        verbose_name_plural = "Портфолио ученых"
        ordering = ["order"]

class Main(models.Model):
    parent = models.ForeignKey("self", related_name="children", on_delete=models.CASCADE, null=True, blank=True)
    image_logo = models.ImageField(upload_to='uploads/', blank=True, null=True)
    title_third_ru = models.CharField("Название университета (рус)", max_length=200)
    title_third_kk = models.CharField("Название университета (каз)", max_length=200, blank=True)
    title_third_en = models.CharField("Название университета (англ)", max_length=200, blank=True)
    title_first_ru = models.CharField("Программы обучения (рус)", max_length=200)
    title_first_kk = models.CharField("Программы обучения (каз)", max_length=200, blank=True)
    title_first_en = models.CharField("Программы обучения (англ)", max_length=200, blank=True)
    card_image_url = models.CharField("Ссылка на картинку", max_length=100, blank=True, null=True)
    title_second_ru = models.CharField("Смотреть все программы (рус)", max_length=200)
    title_second_kk = models.CharField("Смотреть все программы (каз)", max_length=200, blank=True)
    title_second_en = models.CharField("Смотреть все программы (англ)", max_length=200, blank=True)
    title_fourth_ru = models.CharField("Текст подать заявление (рус)", max_length=200)
    title_fourth_kk = models.CharField("Текст подать заявление (каз)", max_length=200, blank=True)
    title_fourth_en = models.CharField("Текст подать заявление (англ)", max_length=200, blank=True)
    title_fifth_ru = models.CharField("Заголовок новостей (рус)", max_length=200)
    title_fifth_kk = models.CharField("Заголовок новостей (каз)", max_length=200, blank=True)
    title_fifth_en = models.CharField("Заголовок новостей (англ)", max_length=200, blank=True)
    title_tenth_ru = models.CharField("Заголовок ректора (рус)", max_length=200, blank=True)
    title_tenth_kk = models.CharField("Заголовок ректора (каз)", max_length=200, blank=True)
    title_tenth_en = models.CharField("Заголовок ректора (англ)", max_length=200, blank=True)
    rector_image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    title_sixth_ru = models.CharField("ФИО ректора (рус)", max_length=200)
    title_sixth_kk = models.CharField("ФИО ректора (каз)", max_length=200, blank=True)
    title_sixth_en = models.CharField("ФИО ректора (англ)", max_length=200, blank=True)
    title_seventh_ru = models.CharField("Должность ректора (рус)", max_length=200)
    title_seventh_kk = models.CharField("Должность ректора (каз)", max_length=200, blank=True)
    title_seventh_en = models.CharField("Должность ректора (англ)", max_length=200, blank=True)
    title_eighth_ru = models.CharField("Звание ректора (рус)", max_length=200)
    title_eighth_kk = models.CharField("Звание ректора (каз)", max_length=200, blank=True)
    title_eighth_en = models.CharField("Звание ректора (англ)", max_length=200, blank=True)
    title_ninth_ru = models.CharField("Задать вопрос ректору текст (рус)", max_length=200)
    title_ninth_kk = models.CharField("Задать вопрос ректору текст (каз)", max_length=200, blank=True)
    title_ninth_en = models.CharField("Задать вопрос ректору текст (англ)", max_length=200, blank=True)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    url = models.CharField("Ссылка", max_length=100, blank=True, null=True)
    rector_url = models.CharField("Ссылка", max_length=100, blank=True, null=True)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Главная страница (путь - /home/)"
        verbose_name_plural = "Главная страница"
        ordering = ["order"]


class ProgramCard(models.Model):
    main = models.ForeignKey(
        Main,
        related_name="cards",
        on_delete=models.CASCADE
    )

    image = models.ImageField(upload_to='uploads/', blank=True, null=True)

    title_ru = models.CharField(max_length=200)
    title_kk = models.CharField(max_length=200, blank=True)
    title_en = models.CharField(max_length=200, blank=True)

    summary_ru = models.TextField()
    summary_kk = models.TextField(blank=True)
    summary_en = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

class InstructionCard(models.Model):
    header = models.ForeignKey(Main, related_name="headers", on_delete=models.CASCADE)
    content_rus = RichTextField("Содержание (рус)", blank=True, null=True)
    content_kaz = RichTextField("Содержание (каз)", blank=True, null=True)
    content_eng = RichTextField("Содержание (англ)", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ["order"]
    
class HeaderMain(models.Model):
    title_ru = models.CharField(verbose_name="Заголовок в header (рус)", blank=True, null=True)
    title_kk = models.CharField("Заголовок в header(каз)", max_length=200, blank=True)
    title_en = models.CharField("Заголовок в header (англ)", max_length=200, blank=True)
    image_logo = models.ImageField(upload_to='uploads/', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Оформление сотрудника (заголовок)"
        verbose_name_plural = "Оформление сотрудника (заголовок)"

class ScienceDepartmentImages(models.Model):
    title_second_ru = models.CharField("Второй заголовок (рус)", max_length=200, blank=True, default="")
    title_second_kk = models.CharField("Второй заголовок (каз)", max_length=200, blank=True, default="")
    title_second_en = models.CharField("Второй заголовок (англ)", max_length=200, blank=True, default="")
    within_modal_ru = models.CharField("Заголовок модалки (рус)", max_length=200, blank=True, default="")
    within_modal_kk = models.CharField("Заголовок модалки (каз)", max_length=200, blank=True, default="")
    within_modal_en = models.CharField("Заголовок модалки (англ)", max_length=200, blank=True, default="")
    url = models.CharField("Ссылка_1", max_length=100, blank=True, null=True)
    url_download = models.CharField("Ссылка_3", max_length=100, blank=True, null=True)
    order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Картинки"
        verbose_name_plural = "Картинки Департамента науки"
        ordering = ["order"]

class ScienceDepartmentText(models.Model):
    title_ru = RichTextField("Содержание (рус)", blank=True, null=True)
    title_kk = RichTextField("Содержание (каз)", blank=True, null=True)
    title_en = RichTextField("Содержание (англ)", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Текст"
        verbose_name_plural = "Текст Департамента науки"

class ScienceDepartmentModule(models.Model):
    parent = models.ForeignKey("self",related_name="children",on_delete=models.CASCADE,null=True,blank=True,verbose_name="Родитель")
    title_ru = models.CharField("Заголовок модалки (рус)", max_length=200, blank=True, default="")
    title_kk = models.CharField("Заголовок модалки (каз)", max_length=200, blank=True, default="")
    title_en = models.CharField("Заголовок модалки (англ)", max_length=200, blank=True, default="")
    title_second_ru = models.CharField("Заголовок внутри модалки (рус)", max_length=200, blank=True, default="")
    title_second_kk = models.CharField("Заголовок внутри модалки (каз)", max_length=200, blank=True, default="")
    title_second_en = models.CharField("Заголовок внутри модалки (англ)", max_length=200, blank=True, default="")
    title_third_ru = models.CharField("Текст внутри модалки (рус)", max_length=200, blank=True, default="")
    title_third_kk = models.CharField("Текст внутри модалки (каз)", max_length=200, blank=True, default="")
    title_third_en = models.CharField("Текст внутри модалки (англ)", max_length=200, blank=True, default="")
    url = models.CharField("Ссылка", max_length=100, blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Модалка"
        verbose_name_plural = "Модалки Департамента науки"

class ScienceDepartmentFile(models.Model):
    title_ru = models.CharField("Текст (рус)", max_length=200, blank=True, default="")
    title_kk = models.CharField("Текст (каз)", max_length=200, blank=True, default="")
    title_en = models.CharField("Текст (англ)", max_length=200, blank=True, default="")
    url = models.CharField("Ссылка", max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Файл"
        verbose_name_plural = "Файлы Департамента науки"

class ScienceDepartmentLink(models.Model):
    title_ru = models.CharField("Текст (рус)", max_length=200, blank=True, default="")
    title_kk = models.CharField("Текст (каз)", max_length=200, blank=True, default="")
    title_en = models.CharField("Текст (англ)", max_length=200, blank=True, default="")
    url = models.CharField("Ссылка", max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Ссылка"
        verbose_name_plural = "Ссылки Департамента науки"

class Accreditation(models.Model):
    image = models.ImageField(upload_to="uploads/", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Аккредитация образовательных программ"
        verbose_name_plural = "Аккредитация образовательных программ"

class Polozhenia(models.Model):
    title_ru = models.CharField("Заголовок (рус)", max_length=200, blank=True, default="")
    title_kk = models.CharField("Заголовок (каз)", max_length=200, blank=True, default="")
    title_en = models.CharField("Заголовок (англ)", max_length=200, blank=True, default="")
    title_second_ru = models.CharField("Текст (рус)", max_length=200, blank=True, default="")
    title_second_kk = models.CharField("Текст (каз)", max_length=200, blank=True, default="")
    title_second_en = models.CharField("Текст (англ)", max_length=200, blank=True, default="")
    url = models.CharField("Ссылка", max_length=300, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Положения"
        verbose_name_plural = "Положения"

class Academic(models.Model):
    title_ru = models.CharField("Текст (рус)", max_length=200, blank=True, default="")
    title_kk = models.CharField("Текст (каз)", max_length=200, blank=True, default="")
    title_en = models.CharField("Текст (англ)", max_length=200, blank=True, default="")
    university_name = models.CharField("Наименование университета", max_length=200, blank=True, default="")
    partner_type = models.CharField("Тип партнера", max_length=200, blank=True, default="")
    lat = models.FloatField(verbose_name="Широта", null=True, blank=True, default=0.0)
    lang = models.FloatField(verbose_name="Долгота", null=True, blank=True, default=0.0)
    university_web_site = models.CharField("Ссылка на университет", max_length=300, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Вузы-партнеры"
        verbose_name_plural = "Вузы-партнеры"

class Candidates(models.Model):
    parent = models.ForeignKey("self", related_name="children", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Родитель")
    title_ru = models.CharField("Текст (рус)", max_length=200, blank=True, default="")
    title_kk = models.CharField("Текст (каз)", max_length=200, blank=True, default="")
    title_en = models.CharField("Текст (англ)", max_length=200, blank=True, default="")
    title_second_ru = RichTextField("Содержание (рус)", blank=True, null=True)
    title_second_kk = RichTextField("Содержание (каз)", blank=True, null=True)
    title_second_en = RichTextField("Содержание (англ)", blank=True, null=True)
    title_third_ru = models.CharField("Текст с сылкой (рус)", max_length=200, blank=True, default="")
    title_third_kk = models.CharField("Текст с сылкой (каз)", max_length=200, blank=True, default="")
    title_third_en = models.CharField("Текст с сылкой (англ)", max_length=200, blank=True, default="")
    url = models.CharField("Ссылка", max_length=300, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Кандидаты на научные звания"
        verbose_name_plural = "Кандидаты на научные звания"

class Footer(models.Model):
    summary_ru = models.CharField("Содержание (рус)", max_length=200, blank=True, default="")
    summary_kk = models.CharField("Содержание (каз)", max_length=200, blank=True, default="")
    summary_en = models.CharField("Содержание (англ)", max_length=200, blank=True, default="")
    image = models.ImageField(upload_to="uploads/", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Подвал"
        verbose_name_plural = "Подвал"

class FooterSection(models.Model):
    block = models.ForeignKey(
        Footer,
        related_name="sections",
        null=True, 
        blank=True,
        on_delete=models.CASCADE
    )

    parent = models.ForeignKey(
        "self",
        related_name="children",
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    # Заголовок колонки
    title_ru = models.CharField(max_length=200, blank=True, null=True, default="")
    title_kk = models.CharField(max_length=200, blank=True, null=True, default="")
    title_en = models.CharField(max_length=200, blank=True, null=True, default="")

    # Текст ссылки
    summary_ru = models.CharField(max_length=200, blank=True, null=True, default="")
    summary_kk = models.CharField(max_length=200, blank=True, null=True, default="")
    summary_en = models.CharField(max_length=200, blank=True, null=True, default="")

    url = models.CharField(max_length=300, null=True, blank=True)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

class FooterUrl(models.Model):
    block = models.ForeignKey(Footer, related_name="urls", blank=True, null=True, on_delete=models.CASCADE)
    image_logo = models.ImageField(upload_to="uploads/", blank=True, null=True)
    url = models.CharField("Ссылка", max_length=300, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

#class Yarmarka(models.Model):
#    title_ru = models.CharField(max_length=200, blank=True, null=True, default="")
#    title_kk = models.CharField(max_length=200, blank=True, null=True, default="")
#    title_en = models.CharField(max_length=200, blank=True, null=True, default="")
#    second_title_ru = models.CharField(max_length=200, blank=True, null=True, default="")
#    second_title_kk = models.CharField(max_length=200, blank=True, null=True, default="")
#    second_title_en = models.CharField(max_length=200, blank=True, null=True, default="")
#    order = models.PositiveIntegerField("Порядок", default=0)
#    is_active = models.BooleanField("Активен", default=True)
#    
#class YarmarkaTexts(models.Model):
#    title_ru = models.CharField(max_length=200, blank=True, null=True, default="")
#    title_kk = models.CharField(max_length=200, blank=True, null=True, default="")
#    title_en = models.CharField(max_length=200, blank=True, null=True, default="")

# Новый проект
class HeadHunterModel(models.Model):
    title_ru = RichTextField("Содержание (рус)", blank=True, null=True)
    url = models.CharField("Ссылка", max_length=300, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Элементы заголовков"
        verbose_name_plural = "Элементы заголовков"

class HHProfile(models.Model):
    title_ru = RichTextField("Содержание (рус)", blank=True, null=True)
    url = models.CharField("Ссылка", max_length=300, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профиль"

class HHLogo(models.Model):
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Логотип"
        verbose_name_plural = "Логотип"

class HHJobVacancyTitle(models.Model):
    title = models.CharField(verbose_name='Заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Список профессий (заголовки)"
        verbose_name_plural = "Список профессий (заголовки)"

class HHJobVacancySecondTitle(models.Model):
    title = models.CharField(verbose_name='Второй заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Список профессий (нижний заголовок)"
        verbose_name_plural = "Список профессий (нижний заголовок)"

class HHJobVacancyDropdown(models.Model):
    title = models.CharField(verbose_name='Заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Список профессий (выпадающий список)"
        verbose_name_plural = "Список профессий (выпадающий список)"

class HHJobExperienceHeader(models.Model):
    title = models.CharField(verbose_name='Заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Опыт работы (заголовок)"
        verbose_name_plural = "Опыт работы (заголовок)"

class HHJobExperienceUnderHeader(models.Model):
    title = models.CharField(verbose_name='Заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Опыт работы (нижний заголовок)"
        verbose_name_plural = "Опыт работы (нижний заголовок)"

class HHJobExperienceSummary(models.Model):
    title = models.CharField(verbose_name='Заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Опыт работы (содержание)"
        verbose_name_plural = "Опыт работы (содержание)"

class HHJobConditionsHeader(models.Model):
    title = models.CharField(verbose_name='Заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Условия работы (заголовок)"
        verbose_name_plural = "Условия работы (заголовок)"

class HHJobConditionsUnderHeader(models.Model):
    title = models.CharField(verbose_name='Заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Условия работы (нижний заголовок)"
        verbose_name_plural = "Условия работы (нижний заголовок)"

class HHJobConditionsSummary(models.Model):
    parent = models.ForeignKey(HHJobConditionsUnderHeader, related_name="children", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Родитель")
    title = models.CharField(verbose_name='Заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Условия работы (содержание)"
        verbose_name_plural = "Условия работы (содержание)"

class HHWorkHeader(models.Model):
    title = models.CharField(verbose_name='Заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Формат работы (заголовок)"
        verbose_name_plural = "Формат работы (заголовок)"

class HHWorkUnderHeader(models.Model):
    parent = models.ForeignKey(HHWorkHeader, related_name="children", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Родитель")
    title = models.CharField(verbose_name='Заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Формат работы (чекбоксы)"
        verbose_name_plural = "Формат работы (чекбоксы)"

class HHEmployerHeader(models.Model):
    title = models.CharField(verbose_name='Заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Оформление сотрудника (заголовок)"
        verbose_name_plural = "Оформление сотрудника (заголовок)"

class HHEmployerUnderHeader(models.Model):
    parent = models.ForeignKey(HHEmployerHeader, related_name="children", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Родитель")
    parent_header = models.ForeignKey("self", related_name="children", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Родитель")
    title = models.CharField(verbose_name='Заголовок страницы вакансий', blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0)
    is_active = models.BooleanField(verbose_name='', default=True)

    class Meta:
        verbose_name = "Оформление сотрудника (чекбоксы и нижний заголовок)"
        verbose_name_plural = "Оформление сотрудника (чекбоксы и нижний заголовок)"

class News(models.Model):

    CATEGORY_CHOICES = [
        (
            "news",
            "news — Международные конкурсы, гранты, научно-исследовательские и образовательные стажировки",
        ),
        (
            "news-international",
            "news-international — Международное сотрудничество",
        ),
        (
            "news-main",
            "news-main — Новости главной страницы",
        ),
    ]

    category_slug = models.SlugField(
        max_length=200,
        db_index=True,
        choices=CATEGORY_CHOICES,
        verbose_name="Категория",
    )

    category_title = models.CharField(
        max_length=200,
        editable=False,
        verbose_name="Category title",
    )

    title = models.CharField(
        max_length=500,
        blank=True,
        help_text='Необязательно для заполнения. Используется как ориентир.'
    )

    slug = models.SlugField(
        max_length=500,
        unique=True
    )

    content_rus = RichTextField("Содержание (рус)", max_length=100000, blank=True, null=True)

    content_kaz = RichTextField("Содержание (каз)", max_length=100000, blank=True, null=True)

    content_eng = RichTextField("Содержание (англ)", max_length=100000, blank=True, null=True)
    
    # tag = models.CharField(max_length=200, editable=False, verbose_name="Category title",)
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        verbose_name="",
        default=True
    )

    def save(self, *args, **kwargs):
        self.category_title = self.category_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class NewsImage(models.Model):
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='uploads/news/')
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.news.title} — изображение {self.order}"


class SDGContactMessage(models.Model):
    name = models.CharField("Имя", max_length=150)
    email = models.EmailField("E-mail")
    subject = models.CharField("Тема", max_length=255, blank=True)
    message = models.TextField("Сообщение")
    consent = models.BooleanField("Согласие на обработку данных", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    is_processed = models.BooleanField("Обработано", default=False)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Обращение в проектный офис ЦУР"
        verbose_name_plural = "Обращения в проектный офис ЦУР"

    def __str__(self):
        return f"{self.name}: {self.subject or 'Без темы'}"
