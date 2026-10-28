# forms.py
from django import forms
from .models import Page, SDGContactMessage
from ckeditor.widgets import CKEditorWidget

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'content']
        widgets = {
            'content': CKEditorWidget(),  # Здесь указываем виджет CKEditor
        }


class SDGContactForm(forms.ModelForm):
    consent = forms.BooleanField(
        required=True,
        label="Я согласен(на) на обработку персональных данных",
        error_messages={"required": "Необходимо согласие на обработку данных."},
    )

    class Meta:
        model = SDGContactMessage
        fields = ("name", "email", "subject", "message", "consent")
        labels = {
            "name": "Ваше имя",
            "email": "E-mail",
            "subject": "Тема обращения",
            "message": "Сообщение",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Имя", "autocomplete": "name"}),
            "email": forms.EmailInput(
                attrs={"placeholder": "name@example.com", "autocomplete": "email"}
            ),
            "subject": forms.TextInput(
                attrs={"placeholder": "Партнёрство, проект или вопрос"}
            ),
            "message": forms.Textarea(
                attrs={"placeholder": "Расскажите о вашей инициативе", "rows": 5}
            ),
        }

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        compact_message = " ".join(message.split())
        if len(compact_message) < 10:
            raise forms.ValidationError("Сообщение должно содержать не менее 10 символов.")
        if len(message) > 5000:
            raise forms.ValidationError("Сообщение не должно превышать 5000 символов.")
        return message
