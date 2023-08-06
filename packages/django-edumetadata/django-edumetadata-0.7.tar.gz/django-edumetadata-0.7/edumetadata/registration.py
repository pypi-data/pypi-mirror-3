from collections import defaultdict

from django.db.models import FieldDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model, ForeignKey, ManyToManyField

from edumetadata.settings import FK_REGISTRY, M2M_REGISTRY, HISTORICAL_DATE_FIELDS
from edumetadata.fields import HistoricalDateField

# The field registry keeps track of the individual fields created.
#  {'app.model.field': Field(**extra_params)}
#  Useful for doing a schema migration
FIELD_REGISTRY = {}

# The model registry keeps track of which models have one or more fields
# registered.
# {'app': [model1, model2]}
# Useful for admin alteration
MODEL_REGISTRY = defaultdict(list)


def register_m2m(model, field_name, extra_params={}):
    return _register(model, field_name, extra_params, ManyToManyField)


def register_fk(model, field_name, extra_params={}):
    return _register(model, field_name, extra_params, ForeignKey)


def _register(model, field_name, extra_params={}, field=ForeignKey):
    app_label = model._meta.app_label
    registry_name = ".".join((app_label, model.__name__, field_name)).lower()

    if registry_name in FIELD_REGISTRY:
        return
    opts = model._meta
    try:
        opts.get_field(field_name)
    except FieldDoesNotExist:
        if app_label not in MODEL_REGISTRY:
            MODEL_REGISTRY[app_label] = []
        if model not in MODEL_REGISTRY[app_label]:
            MODEL_REGISTRY[app_label].append(model)
        FIELD_REGISTRY[registry_name] = field(**extra_params)
        FIELD_REGISTRY[registry_name].contribute_to_class(model, field_name)


def handle_prepared_model(sender, *args, **kwargs):
    """
    Listens to django.db.models.signals.class_prepared and checks to see if the
    class is configured to insert FK or M2M fields.
    """
    app_label = sender._meta.app_label
    sender_name = "%s.%s" % (sender._meta.app_label, sender._meta.module_name)

    err = "EDUMETADATA['FK_REGISTRY'] doesn't recognize the value of %s"
    for default_name, config in FK_REGISTRY.items():
        registered_models = [key.lower() for key in config.keys()]
        if sender_name not in registered_models:
            continue
        to_model = config.pop('to')
        for key, value in config.items():
            model = sender
            if model is None:
                raise ImproperlyConfigured('%s is not a model' % key)
            if isinstance(value, (tuple, list)):
                for item in value:
                    if isinstance(item, basestring):
                        # print "Adding %s to model %s" % (item, sender_name)
                        register_fk(model, item, extra_params={'to': to_model})
                    elif isinstance(item, dict):
                        field_name = item.pop('name')
                        # print "Adding %s to model %s" % (field_name, sender_name)
                        item.update({'to': to_model})
                        register_fk(model, field_name, extra_params=item)
                    else:
                        raise ImproperlyConfigured(err % key)
            elif isinstance(value, basestring):
                # print "Adding %s to model %s" % (value, sender_name)
                register_fk(model, value, extra_params={'to': to_model})
            elif isinstance(value, dict):
                field_name = value.pop('name')
                value.update({'to': to_model})
                # print "Adding %s to model %s" % (field_name, sender_name)
                register_fk(model, field_name, extra_params=value)
            else:
                raise ImproperlyConfigured(err % key)
        del FK_REGISTRY[default_name]

    err = "EDUMETADATA['M2M_REGISTRY'] doesn't recognize the value of %s: %s"
    for default_name, config in M2M_REGISTRY.items():
        registered_models = [key.lower() for key in config.keys()]
        if sender_name not in registered_models:
            continue
        to_model = config.pop('to')
        for key, value in config.items():
            if app_label != key.split('.')[0]:
                continue
            model = sender
            if model is None:
                raise ImproperlyConfigured('%s is not a model' % key)
            if isinstance(value, (tuple, list)):
                for item in value:
                    if isinstance(item, basestring):
                        register_m2m(model, item, extra_params={'to': to_model})
                    elif isinstance(item, dict):
                        field_name = item.pop('name')
                        item.update({'to': to_model})
                        register_m2m(model, field_name, extra_params=item)
                    else:
                        raise ImproperlyConfigured(err % (key, item))
            elif isinstance(value, basestring):
                register_m2m(model, value, extra_params={'to': to_model})
            elif isinstance(value, dict):
                field_name = value.pop('name')
                item.update({'to': to_model})
                register_m2m(model, field_name, extra_params=value)
            else:
                raise ImproperlyConfigured(err % key)

    for key, value in HISTORICAL_DATE_FIELDS.items():
        if app_label != key.split('.')[0]:
            continue
        model = get_model(*key.split('.'))
        if model is None:
            raise ImproperlyConfigured('%s is not a model' % key)
        if isinstance(value, (tuple, list)):
            for item in value:
                if isinstance(item, basestring):
                    _register(model, item, field=HistoricalDateField)
                elif isinstance(item, dict):
                    field_name = item.pop('name')
                    _register(model, field_name, extra_params=item, field=HistoricalDateField)
                else:
                    raise ImproperlyConfigured("EDUMETADATA_'HISTORICAL_DATE_FIELDS'] doesn't recognize the value of %s" % key)
        elif isinstance(value, basestring):
            _register(model, value, field=HistoricalDateField)
        elif isinstance(item, dict):
            field_name = item.pop('name')
            _register(model, field_name, extra_params=item, field=HistoricalDateField)
        else:
            raise ImproperlyConfigured("EDUMETADATA_'HISTORICAL_DATE_FIELDS'] doesn't recognize the value of %s" % key)
