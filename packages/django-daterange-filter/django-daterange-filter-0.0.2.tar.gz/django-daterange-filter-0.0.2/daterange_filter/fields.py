# -*- coding: utf-8 -*-


'''
Overrides the ``django.db.models.DateField`` and
``django.db.models.DateTimeField`` so they can use the ``django.conf.settings``
values to convert into python.

This was required because on the admin, when filtering by date the only allowed
format is: '%Y-%m-%d'. So I extend the field classes to use the settings
configuration values if required.
'''

from django.conf import settings
from django.core import exceptions
from django.db import models
from datetime import datetime

from south.modelsinspector import add_introspection_rules


class DateRangeField(models.DateField):

    def get_prep_lookup(self, lookup_type, value):
        try:
            return super(DateRangeField, self).get_prep_lookup(lookup_type,
                                                               value)
        except exceptions.ValidationError, e:
            if isinstance(value, basestring):
                for format in settings.DATE_INPUT_FORMATS:
                    try:
                        return datetime.strptime(value, format).date()
                    except:
                        pass

            raise e


class DateTimeRangeField(models.DateTimeField):

    def get_prep_lookup(self, lookup_type, value):
        try:
            return super(DateTimeRangeField, self).get_prep_lookup(lookup_type,
                                                                   value)
        except exceptions.ValidationError, e:
            if isinstance(value, basestring):
                for format in settings.DATETIME_INPUT_FORMATS:
                    try:
                        return datetime.strptime(value, format)
                    except:
                        pass

            raise e


add_introspection_rules([], ["^daterange_filter\.fields\.DateRangeField"])
add_introspection_rules([], ["^daterange_filter\.fields\.DateTimeRangeField"])
