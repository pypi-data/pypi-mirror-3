from itertools import groupby
import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.importlib import import_module

try:
    from simplejson import load
except ImportError:
    from json import load


def register_app(app_label):
    model_list = models.get_models(app_label)
    register_model(*model_list)


def _is_synced(*mods):
    from django.db import connection
    all_tables = connection.introspection.table_names()
    converter = connection.introspection.table_name_converter
    return set(converter(x._meta.db_table) for x in mods).issubset(all_tables)


def use_database():
    has_setting = hasattr(settings, "HELPTEXT_USE_DATABASE")
    return not has_setting or settings.HELPTEXT_USE_DATABASE
    

def register_model(*model_list):
    if not ContentType._meta.installed:
        raise ImproperlyConfigured(
            "Put 'django.contrib.contenttypes' in your INSTALLED_APPS setting "
            "in order to use the helptext application.")

    if not _is_synced(ContentType):
        return
    use_field_help_table = use_database() and _is_synced(FieldHelp)

    for model in model_list:
        for mod, fields in groupby(model._meta.get_fields_with_model(),
                                   lambda x: x[1]):
            if mod is None:
                mod = model
            if not _is_synced(mod):
                # probably not synced yet
                continue
            fields = [x[0] for x in fields]

            content_type = ContentType.objects.get_for_model(mod)
            can_help_text = lambda f: all((
                f.editable,
                not f.auto_created,
                not isinstance(f.help_text, FieldHelpProxy),))
            for field in (f for f in fields if can_help_text(f)):
                fh = None
                if use_field_help_table:
                    fhs = FieldHelp.objects.filter(content_type=content_type,
                                                   field_name=field.name)
                    if fhs:
                        assert len(fhs) == 1
                        fh = fhs[0]
                        if fh.original_help_text != field.help_text:
                            fh.original_help_text = field.help_text
                            fh.save()
                if not fh:
                    fh = FieldHelp(content_type=content_type,
                                   field_name=field.name,
                                   help_text='',
                                   original_help_text=field.help_text)
                    if use_field_help_table:
                        fh.save()
                field.help_text = FieldHelpProxy(fh)


class FieldHelpProxy(object):

    def __init__(self, fh):
        self.original_fh = fh
        self.content_type = fh.content_type
        self.field_name = fh.field_name

    def __unicode__(self):
        # The database table exists if an only if the original fh has a pk.
        if self.original_fh.pk:
            try:
                # Don't use the original FieldHelp in case the database changed
                fh = FieldHelp.objects.get(content_type=self.content_type,
                                           field_name=self.field_name)
                return fh.get_help_text()
            except FieldHelp.DoesNotExist:
                # shouldn't happen
                return self.original_fh.get_non_db_help_text()
        else:
            return self.original_fh.get_non_db_help_text()


_configuration = None


def get_configuration():
    global _configuration
    if _configuration is None:
        path = getattr(settings, 'HELPTEXT_CONFIGURATION', '')
        # if we error out in trying to get the config, we
        # use this value as a sentinel
        _configuration = {}
        if path:
            # we'll be lenient for a non-existent path, but if the
            # path exists and isn't any good, we'll blow up.
            if not os.path.exists(path):
                import warnings
                warnings.warn("helptext configuration not found at %s" % path,
                              RuntimeWarning)
            else:
                # let IOError or ValueError propagate
                tmp = load(open(path))
                if not isinstance(tmp, dict):
                    msg = "%s should consist of a single json hashtable."
                    raise ImproperlyConfigured(msg % path)
                else:
                    # we're good, save the global
                    _configuration = tmp
    return _configuration


class FieldHelp(models.Model):
    content_type = models.ForeignKey(ContentType)
    field_name = models.CharField(max_length=120)
    help_text = models.TextField(blank=True)
    original_help_text = models.TextField(blank=True)

    def get_help_text(self):
        return self.help_text or self.get_non_db_help_text()

    def get_non_db_help_text(self):
        return self.get_configured_help_text() or self.original_help_text
        
    def get_configured_help_text(self):
        helptext_configuration = get_configuration()
        if helptext_configuration:
            return helptext_configuration.get(self.lookup_key(), "")
        return ""

    @property
    def model(self):
        return self.content_type.model_class()

    @property
    def field(self):
        return self.model._meta.get_field(self.field_name)

    def app_title(self):
        return self.model._meta.app_label.title()
    app_title.short_description = 'Application'

    def model_title(self):
        return self.model._meta.verbose_name.title()
    model_title.short_description = 'Model'

    def field_title(self):
        return self.field.verbose_name.title()
    field_title.short_description = 'Field'

    def lookup_key(self):
        args = (self.app_title(), self.model_title(), self.field_title(),)
        return "%s.%s.%s" % args

    class Meta:
        ordering = ('content_type', 'field_name')
        unique_together = (('content_type', 'field_name'),)
        verbose_name_plural = "Field Help"

    def __repr__(self):
        return '<FieldHelp for %r: %r>' % \
               (self.content_type.name,
                self.help_text)

    def __unicode__(self):
        return u"%s - %s: %s" % (self.model._meta.app_label.title(),
                                 self.model._meta.verbose_name.title(),
                                 self.field.verbose_name.title())

    def delete(self):
        self.field.help_text = self.original_help_text
        super(FieldHelp, self).delete()
