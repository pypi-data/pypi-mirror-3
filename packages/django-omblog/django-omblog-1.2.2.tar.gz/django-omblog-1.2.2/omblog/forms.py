from django import forms
from omblog.models import Post

class PostForm(forms.ModelForm):

    class Meta:
        model = Post

    class Media:
        css = {
            'all': ('omblog/css/omblog.writing.css',)
        }
        js = ('omblog/js/omblog.writing.js',)
