from django import forms
from django.utils.safestring import mark_safe

class CKEditor5Widget(forms.Textarea):
    class Media:
        # Подключаем JS для CKEditor 5
        js = ('ckeditor5-build-classic/ckeditor.js',)  # путь к вашему ckeditor.js
        css = {
            'all': ('ckeditor5-build-classic/styles.css',)  # путь к стилям CKEditor
        }

    def render(self, name, value, attrs=None, renderer=None):
        # Генерация обычного textarea
        textarea = super().render(name, value, attrs, renderer)

        # Инициализация CKEditor
        editor_script = f"""
            <script>
                ClassicEditor.create(document.querySelector("#{attrs["id"]}"))
                    .catch(error => console.error(error));
            </script>
        """

        # Возвращаем textarea с подключением скрипта и редактора
        return mark_safe(f'{textarea}{editor_script}')
