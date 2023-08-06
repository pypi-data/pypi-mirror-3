from django.db import models
 
class TranslationForeignKey(models.ForeignKey):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("related_name", "+")
        self.language_code_field = kwargs.pop("language_code_field", "language_code")
        self.translator_name = kwargs.pop("translator", "translation")
        super(TranslationForeignKey, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(TranslationForeignKey, self).contribute_to_class(cls, name)
        cls._meta.unique_together = ((name, self.language_code_field),)
        setattr(self.rel.to, "_translation_foreign_key_field", self)

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], [r"^xadrpy\.i18n\.fields\.TranslationForeignKey"])


