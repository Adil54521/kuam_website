# forms.py
from django import forms
from .models import Page, SDGContactMessage
from ckeditor.widgets import CKEditorWidget

from .sdg_i18n import get_sdg_ui
from .site_language import normalize_language

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

    def __init__(self, *args, language="ru", **kwargs):
        super().__init__(*args, **kwargs)
        self.language = normalize_language(language)
        ui = get_sdg_ui(self.language)

        labels = {
            "name": ui["form_name"],
            "email": ui["form_email"],
            "subject": ui["form_subject"],
            "message": ui["form_message"],
            "consent": ui["form_consent"],
        }
        placeholders = {
            "name": ui["form_name_placeholder"],
            "email": "name@example.com",
            "subject": ui["form_subject_placeholder"],
            "message": ui["form_message_placeholder"],
        }
        for field_name, label in labels.items():
            field = self.fields[field_name]
            field.label = label
            field.error_messages["required"] = ui["form_required"]
            if field_name in placeholders:
                field.widget.attrs["placeholder"] = placeholders[field_name]

        self.fields["email"].error_messages["invalid"] = ui["form_invalid_email"]
        self.fields["consent"].error_messages["required"] = ui[
            "form_consent_required"
        ]
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
        ui = get_sdg_ui(self.language)
        if len(compact_message) < 10:
            raise forms.ValidationError(ui["form_message_short"])
        if len(message) > 5000:
            raise forms.ValidationError(ui["form_message_long"])
        return message
