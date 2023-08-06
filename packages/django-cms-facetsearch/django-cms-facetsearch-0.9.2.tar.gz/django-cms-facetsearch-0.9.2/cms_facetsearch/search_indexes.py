import datetime

from django.conf import settings

from cms.models.pagemodel import Page
from cms.models.titlemodels import Title

from haystack import indexes

from cms_facetsearch.indexes import PluginIndex, Indexable, site

class CmsTitlePluginIndex(PluginIndex, Indexable):
    
    pub_date = indexes.DateTimeField()
    login_required = indexes.BooleanField()
    url = indexes.CharField(stored=True, indexed=False)
    title = indexes.CharField(stored=True, indexed=True)
    
    def get_model(self):
       return Title
       
    def get_placeholders(self, obj, language): 
        return obj.page.placeholders.all()
        
    def prepare_translated(self, obj, language):
        data = super(CmsTitlePluginIndex, self).prepare_translated(obj, language)
        data['title'] = obj.title
        data['pub_date'] = obj.page.publication_date or (datetime.datetime.today() - datetime.timedelta(days=1))
        data['login_required'] = obj.page.login_required
        data['url'] = self.get_absolute_url(obj, language)
        return data
        
    def get_absolute_url(self, obj, language):
        if 'cms.middleware.multilingual.MultilingualURLMiddleware' in settings.MIDDLEWARE_CLASSES:
            return '/%s%s' % (language, obj.page.get_absolute_url())
        else:
            return obj.page.get_absolute_url()        
            
    def index_queryset(self):
        return Title.objects.filter(page__in=Page.objects.published())
        
    def get_index_instance_from_plugin(self, instance, **kwargs):
        try:
            obj = Title.objects.select_related('page').get(page__placeholders__cmsplugin=instance, language=instance.language)
        except Title.DoesNotExist:
            return None
        if obj.page.published:
            return obj
        else:
           return None
           
if getattr(settings, 'CMS_FACETSEARCH_REGISTER_SEARCHINDEX', True):
    
    from cms.models import monkeypatch_reverse
    monkeypatch_reverse()
    
    if site:
        site.register(Title, CmsTitlePluginIndex)