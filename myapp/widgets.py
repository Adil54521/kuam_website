from django import forms
from django.utils.safestring import mark_safe

class CKEditor5Widget(forms.Textarea):
    class Media:
        js = ('ckeditor5/ckeditor.js',)  # путь из STATIC_URL

    def render(self, name, value, attrs=None, renderer=None):
        textarea = super().render(name, value, attrs, renderer)
        script = f'''
        <script>
            ClassicEditor
                .create(document.querySelector('#id_{name}'))
                .catch(error => console.error(error));
        </script>
        '''
        return mark_safe(textarea + script)
