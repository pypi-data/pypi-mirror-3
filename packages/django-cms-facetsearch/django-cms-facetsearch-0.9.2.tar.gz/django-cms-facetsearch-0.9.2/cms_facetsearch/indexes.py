from django.conf import settings
from django.db.models import signals
from django.utils.encoding import force_unicode
from django.utils.html import strip_tags
from django.utils.translation import get_language, activate

from BeautifulSoup import BeautifulStoneSoup
import cgi

from cms.models.pluginmodel import CMSPlugin

from haystack import indexes, __version__ as haystack_version

if haystack_version[:2] < (2, 0):
    from haystack import site
    class Indexable(object):
        pass
else:
    Indexable = indexes.Indexable
    site = None
    
def HTMLEntitiesToUnicode(text):
    """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
    text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
    return text

CELERY_HAYSTACK = 'celery_haystack' in settings.INSTALLED_APPS

IndexBase = indexes.SearchIndex

if CELERY_HAYSTACK:
    from celery_haystack.indexes import CelerySearchIndex
    IndexBase = CelerySearchIndex

class TranslationIndex(IndexBase):
    
    language = indexes.CharField(faceted=True)
    
    def get_language(self, obj):
        return obj.language
        
    def prepare_translated(self, obj, language):
        return {}
        
    def prepare(self, obj):
        current_languge = get_language()
        language = self.get_language(obj)
        try:
            activate(language)
            self.prepared_data = super(TranslationIndex, self).prepare(obj)
            data = self.prepare_translated(obj, language)
            self.prepared_data.update(data)
            return self.prepared_data
        finally:
            activate(current_languge)
            
class PluginIndex(TranslationIndex):
    
    text = indexes.CharField(document=True, use_template=False)

    def get_placeholders(self, obj, language): 
        raise NotImplemented
    
    def get_plugins(self, obj, language):
        placeholders = self.get_placeholders(obj, language)
        return CMSPlugin.objects.filter(language=language, placeholder__in=placeholders)	
                
    def prepare_translated(self, obj, language):
        plugins = self.get_plugins(obj, language)
        data = {'language': language}
        text = ''
        for plugin in plugins:
            instance, _ = plugin.get_plugin_instance()
            if hasattr(instance, 'search_fields'):
                text += u''.join(force_unicode(strip_tags(getattr(instance, field, ''))) for field in instance.search_fields)
            if getattr(instance, 'search_fulltext', False):
                text += strip_tags(instance.render_plugin())
            text = HTMLEntitiesToUnicode(text)
        data['text'] = text
        return data
    
    def get_index_instance_from_plugin(self, instance, **kwargs):
        raise NotImplemented
    
    def enqueue_from_plugin(self, instance, **kwargs):
        if not issubclass(instance.__class__, CMSPlugin) or ('created' in kwargs and kwargs['created']):
            return
        obj = self.get_index_instance_from_plugin(instance, **kwargs)
        if obj:
            self.enqueue("update", obj)
            
    def _setup_save(self, model=None):
        if CELERY_HAYSTACK:    
            super(PluginIndex, self)._setup_save(model=model)
            signals.post_save.connect(self.enqueue_from_plugin)

    def _setup_delete(self, model=None):
        if CELERY_HAYSTACK:
            super(PluginIndex, self)._setup_delete(model=model)
            signals.post_delete.connect(self.enqueue_from_plugin)

    def _teardown_save(self, model=None):
        if CELERY_HAYSTACK:
            super(PluginIndex, self)._teardown_save(model=model)
            signals.post_save.disconnect(self.enqueue_from_plugin)

    def _teardown_delete(self, model=None):
        if CELERY_HAYSTACK:
            super(PluginIndex, self)._teardown_delete(model=model)
            signals.post_delete.disconnect(self.enqueue_from_plugin)