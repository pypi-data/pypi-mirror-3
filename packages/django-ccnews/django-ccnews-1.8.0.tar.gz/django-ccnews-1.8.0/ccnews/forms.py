from django import forms
from writingfield import FullScreenTextarea
from ccnews.models import Article


class ArticleAdminForm(forms.ModelForm):

    class Meta:
        model = Article
        widgets = {
            'content': FullScreenTextarea()
        }


    class Media:
        css = {
                'screen': ('ccnews/css/admin.css',)
            }
