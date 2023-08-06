from django.conf import settings
from django.db.models.signals import class_prepared

DEFAULT_REGISTRY = {
    'grade': {'to': 'edumetadata.Grade'},
    'subject': {'to': 'edumetadata.Subject'},
    'education_category': {'to': 'edumetadata.EducationCategory'},
    'alternate_type': {'to': 'edumetadata.AlternateType'},
    'geologic_time': {'to': 'edumetadata.GeologicTime'},
    'historical_era': {'to': 'edumetadata.HistoricalEra'}
}

DEFAULT_SETTINGS = {
    'ENABLE_GRADES': True,
    'ENABLE_SUBJECTS': True,
    'ENABLE_GEOLOGICTIME': True,
    'ENABLE_ALTTYPES': True,
    'ENABLE_EDUCATEGORIES': True,
    'ENABLE_HISTORICALERAS': True,
    'ERA_TYPE_CHOICES': ((1, 'United States'), (2, 'World')),
    'HISTORICAL_DATE_FIELDS': {},
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(settings, 'EDUMETADATA_SETTINGS', {}))

if 'FK_REGISTRY' in USER_SETTINGS:
    for key in USER_SETTINGS['FK_REGISTRY'].keys():
        USER_SETTINGS['FK_REGISTRY'][key].update(DEFAULT_REGISTRY[key])
else:
    USER_SETTINGS['FK_REGISTRY'] = {}

if 'M2M_REGISTRY' in USER_SETTINGS:
    for key in USER_SETTINGS['M2M_REGISTRY'].keys():
        USER_SETTINGS['M2M_REGISTRY'][key].update(DEFAULT_REGISTRY[key])
else:
    USER_SETTINGS['M2M_REGISTRY'] = {}

globals().update(USER_SETTINGS)

from .registration import handle_prepared_model
class_prepared.connect(handle_prepared_model)
