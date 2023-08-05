from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from models import XXXMODEL_NAMEXXX

class XXXMODEL_NAMEXXXFeed(Feed):
    title = "Latest XXXPLURALXXX"
    description = "Latest XXXPLURALXXX"

    def link(self, obj):
        return reverse('XXXVAR_NAMEXXXs')

    def items(self):
        limit = getattr(settings, 'ITEMS_PER_FEED', 5)
        return XXXMODEL_NAMEXXX.objects.published()[:limit]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content