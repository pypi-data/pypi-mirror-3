from django.conf import settings

from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from haystack.views import search_view_factory, FacetedSearchView

from cms_facetsearch.forms import CmsFacetSearchModelForm

from haystack.query import SearchQuerySet
sqs = SearchQuerySet().facet('language')
view = search_view_factory(view_class=FacetedSearchView, form_class=CmsFacetSearchModelForm, template='search/cms_search.html', searchqueryset=sqs)
        
class DjangoCmsFacetedSearchApphook(CMSApp):
    name = _("Django Cms Faceted Search")
    urls = [patterns('',
        url('^$', view, name='faceted-django-cms-search'),
    ),]

apphook_pool.register(DjangoCmsFacetedSearchApphook)
