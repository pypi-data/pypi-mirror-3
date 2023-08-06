from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ella.core.admin import PublishableAdmin, ListingInlineAdmin
from ella.articles.models import Article


class ArticleAdmin(PublishableAdmin):
    ordering = ('-created',)
    fieldsets = (
        (_("Article heading"), {'fields': ('title', 'upper_title', 'updated', 'slug')}),
        (_("Article contents"), {'fields': ('description', 'content')}),
        (_("Metadata"), {'fields': ('category', 'authors', 'source', 'photo')}),
        (_("Publication"), {'fields': (('publish_from', 'publish_to'), 'static')}),
    )
    inlines = [ListingInlineAdmin]


admin.site.register(Article, ArticleAdmin)
