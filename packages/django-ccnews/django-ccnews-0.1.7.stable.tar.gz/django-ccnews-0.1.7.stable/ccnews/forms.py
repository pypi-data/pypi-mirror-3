from django import forms
from ccnews.models import Article


class ArticleAdminForm(forms.ModelForm):

    class Meta:
        model = Article

    class Media:
        css = {
                'screen': ('ccnews/css/admin.css',)
            }
