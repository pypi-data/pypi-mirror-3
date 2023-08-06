#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides the default settings for the news app
"""

import warnings

from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

DEFAULT_STATUS_CHOICES = (
    (1, _(u'DRAFT')),
    (2, _(u'READY FOR EDITING')),
    (3, _(u'READY TO PUBLISH')),
    (4, _(u'PUBLISHED')),
    (5, _(u'REJECTED')),
    (6, _(u'UN-PUBLISHED')),
)

DEFAULT_ORIGIN_CHOICES = (
    (0, _(u'Admin')),
)

DEFAULT_PAGINATION = {
    'PAGINATE': False,
    'P_PER_PAGE': 20,
    'ORPHANS': 4
}
DEFAULT_QUICKEDIT_FIELDS = (
    'headline',
    'subhead',
    'kicker',
    'status',
    'teaser'
)

DEFAULT_SETTINGS = {
    'AUTHOR_MODEL': 'auth.User',
    'AUTHOR_MODEL_LIMIT_CHOICES': {'is_staff': True},
    'DEFAULT_ORIGIN': 0,
    'DEFAULT_STATUS': 1,
    'ADMIN_EXTRAS': {
        'EXTRA_FIELDSETS': (),
        'RAW_ID_FIELDS': (),
        'FILTER_HORIZONTAL_FIELDS': ('authors',),
        'SEARCH_FIELDS': ('headline',),
        'LIST_PER_PAGE': 25,
    },
    'INCLUDE_PRINT': False,
    'ORDERING': ['-publish_date'],
    'ORIGIN_CHOICES': DEFAULT_ORIGIN_CHOICES,
    'PAGINATION': DEFAULT_PAGINATION,
    'PUBLISHED_STATUS': 4,
    'QUICKEDIT_FIELDS': DEFAULT_QUICKEDIT_FIELDS,
    'RELATION_MODELS': [],
    'STATUS_CHOICES': DEFAULT_STATUS_CHOICES,
    'THROW_404': True,
    'USE_REVERSION': False,
    'WIDGET': None,
    'WIDGET_ATTRS': None
}

USER_SETTINGS = getattr(settings, 'STORY_SETTINGS', {})

DEFAULT_SETTINGS.update(USER_SETTINGS)

error_str = "settings.%s is deprecated; use settings.STORY_SETTINGS instead."

if hasattr(settings, 'STORY_STATUS_CHOICES'):
    warnings.warn(error_str % 'STORY_STATUS_CHOICES', DeprecationWarning)
    DEFAULT_SETTINGS['STATUS_CHOICES'] = getattr(settings, 'STORY_STATUS_CHOICES')

if hasattr(settings, 'STORY_DEFAULT_STATUS'):
    warnings.warn(error_str % 'STORY_DEFAULT_STATUS', DeprecationWarning)
    DEFAULT_SETTINGS['DEFAULT_STATUS'] = getattr(settings, 'STORY_DEFAULT_STATUS')

if hasattr(settings, 'STORY_PUBLISHED_STATUS'):
    warnings.warn(error_str % 'STORY_PUBLISHED_STATUS', DeprecationWarning)
    DEFAULT_SETTINGS['PUBLISHED_STATUS'] = getattr(settings, 'STORY_PUBLISHED_STATUS')

if hasattr(settings, 'STORY_ORIGIN_CHOICES'):
    warnings.warn(error_str % 'STORY_ORIGIN_CHOICES', DeprecationWarning)
    DEFAULT_SETTINGS['ORIGIN_CHOICES'] = getattr(settings, 'STORY_ORIGIN_CHOICES')

if hasattr(settings, 'STORY_INCLUDE_PRINT'):
    warnings.warn(error_str % 'STORY_INCLUDE_PRINT', DeprecationWarning)
    DEFAULT_SETTINGS['INCLUDE_PRINT'] = getattr(settings, 'STORY_INCLUDE_PRINT')

if hasattr(settings, 'STORY_DEFAULT_ORIGIN'):
    warnings.warn(error_str % 'STORY_DEFAULT_ORIGIN', DeprecationWarning)
    DEFAULT_SETTINGS['DEFAULT_ORIGIN'] = getattr(settings, 'STORY_DEFAULT_ORIGIN')

if hasattr(settings, 'STORY_PAGINATION'):
    warnings.warn(error_str % 'STORY_PAGINATION', DeprecationWarning)
    DEFAULT_SETTINGS['PAGINATION']['PAGINATE'] = getattr(settings, 'STORY_PAGINATION')

if hasattr(settings, 'STORY_P_PER_PAGE'):
    warnings.warn(error_str % 'STORY_P_PER_PAGE', DeprecationWarning)
    DEFAULT_SETTINGS['PAGINATION']['P_PER_PAGE'] = getattr(settings, 'STORY_P_PER_PAGE')

if hasattr(settings, 'STORY_ORPHANS'):
    warnings.warn(error_str % 'STORY_ORPHANS', DeprecationWarning)
    DEFAULT_SETTINGS['PAGINATION']['ORPHANS'] = getattr(settings, 'STORY_ORPHANS')

if hasattr(settings, 'STORY_DONT_THROW_404'):
    warnings.warn(error_str % 'STORY_DONT_THROW_404', DeprecationWarning)
    DEFAULT_SETTINGS['THROW_404'] = not getattr(settings, 'STORY_DONT_THROW_404')

if hasattr(settings, 'STORY_RELATION_MODELS'):
    warnings.warn(error_str % 'STORY_RELATION_MODELS', DeprecationWarning)
    DEFAULT_SETTINGS['RELATION_MODELS'] = getattr(settings, 'STORY_RELATION_MODELS') or []


RELATIONS = [Q(app_label=al, model=m) for al, m in [x.split('.') for x in DEFAULT_SETTINGS['RELATION_MODELS']]]

if 'STORY_ORDERING' in DEFAULT_SETTINGS:
    warnings.warn('STORY_ORDERING is being deprecated; use ORDERING instead.', DeprecationWarning)
    DEFAULT_SETTINGS['ORDERING'] = DEFAULT_SETTINGS.pop('STORY_ORDERING')

globals().update(DEFAULT_SETTINGS)
globals().update({'RELATIONS': RELATIONS})
