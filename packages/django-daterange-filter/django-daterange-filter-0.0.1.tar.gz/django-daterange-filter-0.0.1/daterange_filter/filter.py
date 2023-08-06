# -*- coding: utf-8 -*-


'''
Has the filter that allows to filter by a date range.

'''
from django.utils.translation import ugettext as _
from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

class DateForm(forms.Form):

    def __init__(self, *args, **kwargs):
        field_name = kwargs.pop('field_name')
        super(DateForm, self).__init__(*args, **kwargs)
        self.fields['%s__gte' % field_name ] = forms.DateField(label=(_('From')),
                                      widget=AdminDateWidget,
                                      required=False,
                                      input_formats=['%Y-%m-%d'])
        self.fields['%s__lte' % field_name ] = forms.DateField(label=(_('To')),
                                      widget=AdminDateWidget,
                                      required=False,
                                      input_formats=['%Y-%m-%d'])
        for k in kwargs.get('initial',{}):
            if not self.fields.has_key(k):
                self.fields[k] = forms.CharField(widget=forms.HiddenInput())
                self.fields[k].inital = kwargs.get('initial').get(k)


class DateFilterSpec(admin.filters.DateFieldListFilter):

    def __init__(self, f, request, params, model, model_admin, **kwargs):
        super(DateFilterSpec, self).__init__(f, request, params, model,
                                                   model_admin, **kwargs)
        self.field_generic = '%s__' % self.field.name
        self.title = self._title()

    def choices(self, cl):
        return [('A', 'B'),]

    def _title(self):
        form = DateForm(initial=self.date_params, field_name=self.field.name)
        out =  u"""%(field_name)s
        <style>
            .calendarbox {
                left:-400 !important;
                z-index:1100;
        }
        </style>
        <form method="GET" action="">
        <ul>
        %(form)s
        <li> <input type="submit" value="%(search)s"> </li>
        </ul>
        </form>
        """ % {'search':_('Search'),
               'form_media': form.media,
               'form': form.as_p(),
               'admin_media': settings.STATIC_URL,
               'field_name': self.field.verbose_name,
            }
        return mark_safe(out)


# register the filter
admin.filters.FieldListFilter._field_list_filters.insert(0, (
                                lambda f: getattr(f, 'daterange_filter', False),
                                DateFilterSpec))
