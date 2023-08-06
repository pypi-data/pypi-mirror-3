from django.contrib import admin
from ccnews.models import Article, ArticleImage, ArticleAttachment
from ccnews.forms import ArticleAdminForm

class ArticleImageInline(admin.TabularInline):
    model = ArticleImage


class ArticleAttachmentInline(admin.TabularInline):
    model = ArticleAttachment


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    date_hierarchy = 'created'
    prepopulated_fields = {'slug': ('title',)}
    search_fields = (
            'title',
            'content',)
    list_filter = (
            'status',)
    list_display = (
            'title',
            'created',
            'status')
    list_editable = (
            'status',)
    save_on_top = True
    inlines = [
            ArticleImageInline,
            ArticleAttachmentInline]

    fieldsets = (
        (None, {
            'fields': ('status',
                        'title',
                        'content',),
            'classes': ('content',)
        }),
        ('Other Stuff', {
            'fields': ('slug',
                        'created'),
            'classes': ('collapse', 'other')
        })
    )
admin.site.register(Article, ArticleAdmin)
