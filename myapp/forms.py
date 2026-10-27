# forms.py
from django import forms
from .models import Page
from ckeditor.widgets import CKEditorWidget

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'content']
        widgets = {
            'content': CKEditorWidget(),  # Здесь указываем виджет CKEditor
        }
