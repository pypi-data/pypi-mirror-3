from django.db import models
from xadrpy.models.fields.nullchar_field import NullCharField
from xadrpy.models.fields.stringset_field import StringSetField
from django.utils.translation import ugettext_lazy as _
from xadrpy.utils.signals import autodiscover_signal
from django.dispatch.dispatcher import receiver
from django.conf import settings
from inspect import isclass
import libs
from xadrpy.access.models import OwnedModel
from xadrpy.i18n.models import Translation
from xadrpy.i18n.fields import TranslationForeignKey
from xadrpy.models.inheritable import TreeInheritable

class PluginStore(models.Model):
    plugin = models.CharField(max_length=255, unique=True)
    template = NullCharField(max_length=255)
    slots = StringSetField()

    class Meta:
        verbose_name = _("Plugin store")
        verbose_name_plural = _("Plugin store")
        db_table = "xadrpy_templates_plugin_store"

@receiver(autodiscover_signal)
def register_in_store(**kwargs):
    import imp
    from django.utils import importlib

    for app in settings.INSTALLED_APPS:
        
        try:                                                                                                                          
            app_path = importlib.import_module(app).__path__                                                                          
        except AttributeError:                                                                                                        
            continue 
        
        try:                                                                                                                          
            imp.find_module('plugins', app_path)                                                                               
        except ImportError:                                                                                                           
            continue                                                                                                                  
        module = importlib.import_module("%s.plugins" % app)
        for name in dir(module):
            cls = getattr(module,name)
            if isclass(cls) and issubclass(cls, libs.Plugin) and cls!=libs.Plugin:
                store = PluginStore.objects.get_or_create(plugin=cls.get_name())[0]
                if store.template:
                    cls.template = store.template
                libs.PLUGIN_CACHE[cls.get_name()]=cls
                if cls.alias:
                    libs.PLUGIN_CACHE[cls.alias]=cls

class PluginInstance(TreeInheritable, OwnedModel):
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    modified = models.DateTimeField(auto_now=True, verbose_name=_("Modified"))

    plugin = models.CharField(max_length=255)
    placeholder = NullCharField(max_length=255)

    slot = NullCharField(max_length=255)
    position = models.IntegerField(default=1)

    language_code = NullCharField(max_length=5)
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Plugin")
        verbose_name_plural = _("Plugins")
        db_table = "xadrpy_templates_plugin_instance"
    
    def __unicode__(self):
        return self.key
        
class SnippetInstance(PluginInstance):
    body = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Snippet Plugin")
        verbose_name_plural = _("Snippet Plugins")
        db_table = "xadrpy_templates_snippet_instance"

class SnippetTranslation(Translation):
    origin = TranslationForeignKey(SnippetInstance, related_name="+")
    language_code = models.CharField(max_length=5)

    body = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "xadrpy_pages_snippet_instance_translation"

SnippetTranslation.register(SnippetInstance)
