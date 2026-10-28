from django.contrib import admin
from django.contrib.admin import AdminSite
from myapp.models import (BlockText, BlockFile, Block, Page,ProgramCard,
                          MenuItem, Head, Footer, FooterUrl,
                          Bakalavriat, Meropriatia, OfficeCommerse,
                          Learning, LearningCarousel, Research,
                          ResearchModal, Organigramma, Projects,
                          ProjectsModal, Portfolio, PortfolioCategory,
                          Main, ScienceDepartmentImages, ScienceDepartmentText, ScienceDepartmentFile,ScienceDepartmentLink,
                          ScienceDepartmentModule,
                          Accreditation, Polozhenia,
                          Academic, Candidates, HeadHunterModel, HHProfile, HHLogo,
                          HHJobVacancyTitle, HHJobVacancySecondTitle, HHJobVacancyDropdown,
                          HHJobExperienceHeader, HHJobExperienceUnderHeader, HHJobExperienceSummary,
                          HHJobConditionsHeader, HHJobConditionsUnderHeader, HHJobConditionsSummary,
                          HHWorkHeader, HHWorkUnderHeader, HHEmployerHeader, HHEmployerUnderHeader, FooterSection, News, NewsImage, InstructionCard,
                          SDGContactMessage)
from django.utils.safestring import mark_safe
from django import forms
from django.utils.html import format_html, strip_tags
from django.utils.translation import get_language
from ckeditor.widgets import CKEditorWidget

class BlockTextInline(admin.TabularInline):
    model = BlockText
    extra = 1
    fields = ("text_ru", "text_en", "text_kz", "order")
    ordering = ("order",)

class BlockFileInline(admin.TabularInline):
    model = BlockFile
    extra = 1
    fields = ("file", "title", "order", "text_kz", "text_ru", "text_en")
    ordering = ("order",)

class BlockSecondTextInline(admin.TabularInline):
    model = BlockText
    extra = 1
    fields = ("second_text_kk", "second_text_ru", "second_text_en", "order")
    ordering = ("order",)

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("id", "identification")
    inlines = [BlockTextInline, BlockFileInline, BlockSecondTextInline]
        

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = '__all__'
        widgets = {
            'content': CKEditorWidget(attrs={'class': 'ckeditor'}),
        }

class PageAdmin(admin.ModelAdmin):
    form = PageForm
    
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "title_ru",
        "title_kk",
        "title_en",
        "parent",
        "order",
        "is_active",
    )

    list_editable = ("order", "is_active")
    list_filter = ("is_active", "parent")
    search_fields = ("title_ru", "title_kk", "title_en", "url")

    ordering = ("parent", "order")

    fieldsets = (
        ("Названия", {
            "fields": ("title_ru", "title_kk", "title_en")
        }),
        ("Ссылка", {
            "fields": ("url",)
        }),
        ("Структура меню", {
            "fields": ("parent", "order", "css_class")
        }),
        ("Отображение", {
            "fields": ("is_active",)
        }),
    )
admin.site.register(Page, PageAdmin)

@admin.register(Head)
class HeadAdmin(admin.ModelAdmin):
    list_display = (
        "title_ru",
        "order",
        "is_active",
        "css_class",
    )

    list_editable = ("order", "is_active", "css_class")
    list_filter = ("is_active", "css_class")
    search_fields = ("title_ru", "title_kk", "title_en")
    ordering = ("order",)

    fieldsets = (
        ("Фото", {
            "fields": ("image",)
        }),

        ("ФИО", {
            "fields": ("title_ru", "title_kk", "title_en")
        }),

        ("Описание карточки", {
            "fields": ("description_ru", "description_kk", "description_en")
        }),

        ("Отображение", {
            "fields": ("css_class", "order", "is_active")
        }),
    )

@admin.register(Bakalavriat)
class BakalavriatAdmin(admin.ModelAdmin):
    list_display = ("title_kk_title", "title_ru_title", "title_en_title", "title_ru", "title_kk", "title_en", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title_ru", "title_kk", "title_en")
    ordering = ("order",)
    
    fieldsets = (
        ("Заголовок", {"fields": ("title_kk_title", "title_ru_title", "title_en_title")}),
        ("Основная информация", {
            "fields": ("url",)
        }),
        ("Названия (мультиязычные)", {
            "fields": ("title_ru", "title_kk", "title_en")
        }),
        ("Настройки", {
            "fields": ("order", "is_active")
        }),
    )
    
@admin.register(Meropriatia)
class MeropriatiaAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "title_ru", 
        "title_kk", 
        "title_en", 
        "order", 
        "is_active"
    )
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title_ru", "title_kk", "title_en")
    ordering = ("order",)
    list_per_page = 25

    fieldsets = (
        ("Названия", {
            "fields": ("title_ru", "title_kk", "title_en")
        }),
        ("Содержание", {
            "fields": ("summary_ru", "summary_kk", "summary_en")
        }),
        ("Ссылка и отображение", {
            "fields": ("css_class", "order", "is_active")
        }),
    )
    
@admin.register(OfficeCommerse)
class OfficeCommerseAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "title_ru", 
        "title_kk", 
        "title_en", 
        "order", 
        "is_active"
    )
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title_ru", "title_kk", "title_en")
    ordering = ("order",)
    list_per_page = 25

    fieldsets = (
        ("Названия", {
            "fields": ("title_ru", "title_kk", "title_en")
        }),
        ("Ссылка", {
            "fields": ("url",)
        }),
        ("Содержание", {
            "fields": ("summary_ru", "summary_kk", "summary_en")
        }),
        ("Ссылка и отображение", {
            "fields": ("order", "is_active")
        }),
    )

@admin.register(Learning)
class LearningAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title_ru",
        "title_kk",
        "title_en",
        "css_class",
        "order",
        "is_active",
    )
    list_editable = ("order", "is_active", "css_class")
    list_filter = ("is_active", "css_class")
    search_fields = ("title_ru", "title_kk", "title_en", "summary_ru", "summary_kk", "summary_en")
    ordering = ("order",)

    fieldsets = (
        ("Заголовки", {
            "fields": ("title_ru", "title_kk", "title_en"),
        }),
        ("Заголовок под выпадающим списком", {
            "fields": ("summary_title_ru", "summary_title_kk", "summary_title_en"),
        }),
        ("Содержание", {
            "fields": ("summary_ru", "summary_kk", "summary_en"),
        }),
        ("Ссылка и стиль", {
            "fields": ("url", "css_class"),
        }),
        ("Настройки", {
            "fields": ("order", "is_active"),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 50px; border-radius:4px;" />', obj.image.url)
        return "—"

    image_preview.short_description = "Изображение"

@admin.register(LearningCarousel)
class LearningCarouselAdmin(admin.ModelAdmin):
    list_display = ("id", "carousel_img", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "carousel_img")
    search_fields = ("carousel_img_id",)
    ordering = ("order",)


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title_ru",
        "title_kk",
        "title_en",
        "title_summary_ru",
        "title_summary_kk",
        "title_summary_en",
        "order",
        "is_active",
    )
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title_ru", "title_kk", "title_en")
    ordering = ("order",)

    @admin.register(ResearchModal)
    class ResearchModalAdmin(admin.ModelAdmin):
        list_display = (
            "id",
            "parent",
            "title_modal_ru",
            "title_modal_kk",
            "title_modal_en",
            "order",
            "is_active",
        )
        list_editable = ("order", "is_active")
        list_filter = ("is_active", "parent")
        search_fields = ("title_modal_ru", "title_modal_kk", "title_modal_en")
        ordering = ("order",)

@admin.register(Projects)
class ProjectsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title_ru",
        "title_kk",
        "title_en",
        "title_summary_ru",
        "title_summary_kk",
        "title_summary_en",
        "order",
        "is_active",
    )
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title_ru", "title_kk", "title_en")
    ordering = ("order",)

@admin.register(ProjectsModal)
class ProjectsModalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "parent",
        "title_modal_ru",
        "title_modal_kk",
        "title_modal_en",
        "order",
        "is_active",
    )
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "parent")
    search_fields = ("title_modal_ru", "title_modal_kk", "title_modal_en")
    ordering = ("order",)

@admin.register(Organigramma)
class OrganigrammaAdmin(admin.ModelAdmin):
    list_display = (
        'url',
        'order',
        'is_active',
    )

    list_editable = (
        'order',
        'is_active',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'url',
    )

    ordering = (
        'order',
    )

class PortfolioInline(admin.TabularInline):
    model = Portfolio
    extra = 1  # сколько пустых карточек добавлять по умолчанию
    fields = (
        "name_ru", "name_kk", "name_en",
        "image", "summary_ru", "summary_kk", "summary_en",
        "url_email", "url_email_text_ru", "url_email_text_kk", "url_email_text_en",
        "icon", "order", "is_active"
    )
    readonly_fields = ()
    show_change_link = True  # позволяет переходить к полной форме карточки
    ordering = ("order",)

@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("title_ru", "title_kk", "title_en")
    ordering = ("order",)

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "category", "order", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name_ru", "name_kk", "name_en")
    list_editable = ("order", "is_active")
    ordering = ("category", "order")

class ProgramCardInline(admin.TabularInline):
    model = ProgramCard
    extra = 1
    fields = (
        "image",
        "title_ru",
        "title_kk",
        "title_en",
        "summary_ru",
        "summary_kk",
        "summary_en",
        "is_active",
        "order",
    )
    ordering = ("order",)

class InstructionCardInline(admin.StackedInline):
    model = InstructionCard
    extra = 0

    fields = (
        "content_rus",
        "content_kaz",
        "content_eng",
        "is_active",
        "order",
    )

    ordering = ("order",)


@admin.register(Main)
class MainAdmin(admin.ModelAdmin):
    list_display = (
        "title_first_ru",
        "title_second_ru",
        "title_sixth_ru",
        "order",
        "is_active",
    )

    list_editable = (
        "order",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title_first_ru",
        "title_second_ru",
        "title_sixth_ru",
    )

    ordering = (
        "order",
    )

    fieldsets = (
        (
            "Главный блок",
            {
                "fields": (
                    "image_logo",
                    "title_third_ru",
                    "title_third_kk",
                    "title_third_en",
                )
            },
        ),
        (
            "Программы",
            {
                "fields": (
                    "title_first_ru",
                    "title_first_kk",
                    "title_first_en",
                    "title_second_ru",
                    "title_second_kk",
                    "title_second_en",
                )
            },
        ),
        (
            "Кнопка",
            {
                "fields": (
                    "title_fourth_ru",
                    "title_fourth_kk",
                    "title_fourth_en",
                    "url",
                )
            },
        ),
        (
            "Новости",
            {
                "fields": (
                    "title_fifth_ru",
                    "title_fifth_kk",
                    "title_fifth_en",
                )
            },
        ),
        (
            "Ректор",
            {
                "fields": (
                    "title_tenth_ru",
                    "title_tenth_kk",
                    "title_tenth_en",
                    "rector_image",
                    "title_sixth_ru",
                    "title_sixth_kk",
                    "title_sixth_en",
                    "title_seventh_ru",
                    "title_seventh_kk",
                    "title_seventh_en",
                    "title_eighth_ru",
                    "title_eighth_kk",
                    "title_eighth_en",
                    "title_ninth_ru",
                    "title_ninth_kk",
                    "title_ninth_en",
                    "rector_url",
                )
            },
        ),
        (
            "Настройки",
            {
                "fields": (
                    "order",
                    "is_active",
                )
            },
        ),
    )

    inlines = [
        ProgramCardInline,
        InstructionCardInline,
    ]


@admin.register(InstructionCard)
class InstructionCardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "header",
        "order",
        "is_active",
    )

    list_editable = (
        "order",
        "is_active",
    )

    list_filter = (
        "is_active",
        "header",
    )

    search_fields = (
        "content_rus",
        "content_kaz",
        "content_eng",
    )

    ordering = (
        "header",
        "order",
    )
    
@admin.register(ScienceDepartmentImages)
class ScienceDepartmentImagesAdmin(admin.ModelAdmin):
    list_display = ("url_download", "order", "is_active",)
    list_filter = ("is_active",)
    ordering = ("order",)

# 🔹 Inline для файлов внутри модалки
class ScienceDepartmentFileInline(admin.TabularInline):
    model = ScienceDepartmentFile
    extra = 1
    fields = ("title_ru", "title_kk", "title_en", "url", "order", "is_active")
    ordering = ("order",)

# 🔹 Админка для модалок
@admin.register(ScienceDepartmentText)
class ScienceDepartmentTextAdmin(admin.ModelAdmin):
    list_display = ("id", "title_ru", "order", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title_ru", "parent")
    ordering = ("order",)

@admin.register(ScienceDepartmentModule)
class ScienceDepartmentModuleAdmin(admin.ModelAdmin):
    list_display = ("id", "title_ru", "parent", "order", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title_ru", "parent")
    ordering = ("order",)


# 🔹 (опционально) отдельная админка для файлов
@admin.register(ScienceDepartmentFile)
class ScienceDepartmentFileAdmin(admin.ModelAdmin):
    list_display = ("id", "title_ru", "order", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title_ru",)
    ordering = ("order",)

@admin.register(ScienceDepartmentLink)
class ScienceDepartmentLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "title_ru", "order", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title_ru",)
    ordering = ("order",)

@admin.register(Accreditation)
class AccreditationAdmin(admin.ModelAdmin):
    list_display = ("image", "order", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title_ru",)
    ordering = ("order",)

@admin.register(Polozhenia)
class PolozheniaAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "title_kk", "title_en", "title_second_ru", "title_second_kk", "title_second_en", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title_ru",)
    ordering = ("order",)

@admin.register(Academic)
class AcademicAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "title_kk", "title_en", "partner_type", "lat", "lang", "university_web_site", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title_ru",)
    ordering = ("order",)

@admin.register(Candidates)
class CandidatesAdmin(admin.ModelAdmin):
    list_display = ("id", "title_ru", "parent", "order", "is_active")
    list_editable = ("is_active","order")
    list_filter = ("is_active",)
    search_fields = ("title_ru",)
    ordering = ("order",)

class FooterSectionInline(admin.TabularInline):
    model = FooterSection
    extra = 1
    fields = (
        "parent",
        "url",
        "title_ru",
        "title_kk",
        "title_en",
        "summary_ru",
        "summary_kk",
        "summary_en",
        "order",
        "is_active",
    )

class FooterUrlInline(admin.TabularInline):
    model = FooterUrl
    extra = 1
    fields = (
        "image_logo",
        "url",
        "order",
        "is_active",
    )

@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "is_active")
    inlines = [FooterSectionInline, FooterUrlInline]

@admin.register(HeadHunterModel)
class HeadHunterModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title_ru", "order")
    search_fields = ("title_ru",)
    list_editable = ("order",)

@admin.register(HHProfile)
class HHProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "title_ru", "order")
    search_fields = ("title_ru",)
    list_editable = ("order",)

@admin.register(HHLogo)
class HHLogoAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "order")
    search_fields = ("image",)
    list_editable = ("order",)

@admin.register(HHJobVacancyTitle)
class HHJobVacancyTitleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(HHJobVacancySecondTitle)
class HHJobVacancySecondTitleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(HHJobVacancyDropdown)
class HHJobVacancyDropdownAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(HHJobExperienceHeader)
class HHJobExperienceHeaderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(HHJobExperienceUnderHeader)
class HHJobExperienceUnderHeaderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(HHJobExperienceSummary)
class HHJobExperienceSummaryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(HHJobConditionsHeader)
class HHJobConditionsHeaderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(HHJobConditionsUnderHeader)
class HHJobConditionsUnderHeaderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(HHJobConditionsSummary)
class HHJobConditionsSummaryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "parent", "order")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(HHWorkHeader)
class HHWorkHeaderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(HHWorkUnderHeader)
class HHWorkUnderHeaderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(HHEmployerHeader)
class HHEmployerHeaderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(HHEmployerUnderHeader)
class HHEmployerUnderHeaderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "parent", "order")
    search_fields = ("title",)
    list_editable = ("order",)

class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 3
    fields = ('image', 'order')
    ordering = ('order',)
    
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        'content_preview',
        'category_title',
        'created_at',
        'is_active',
    )

    list_filter = (
        'is_active',
        'category_title',
        'created_at',
    )

    search_fields = (
        'content_rus',
        'content_kaz',
        'content_eng',
        'category_title',
    )

    inlines = [
        NewsImageInline,
    ]

    @admin.display(description='Содержание')
    def content_preview(self, obj):
        text = (
            obj.content_rus
            or obj.content_kaz
            or obj.content_eng
            or ''
        )

        text = strip_tags(text)
        text = ' '.join(text.split())

        return text[:120] + '...' if len(text) > 120 else text


@admin.register(NewsImage)
class NewsImageAdmin(admin.ModelAdmin):
    list_display = (
        'news',
        'image',
        'order',
    )

    ordering = (
        'news',
        'order',
    )


@admin.register(SDGContactMessage)
class SDGContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_processed")
    list_filter = ("is_processed", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "consent", "created_at")
    list_editable = ("is_processed",)
    ordering = ("-created_at",)
