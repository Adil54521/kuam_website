# translation.py
from modeltranslation.translator import register, TranslationOptions
from myapp.models import Page

@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')
