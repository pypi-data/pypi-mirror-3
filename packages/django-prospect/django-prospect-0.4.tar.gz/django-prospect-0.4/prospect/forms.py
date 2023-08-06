# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django import forms

from intranet.base_forms import IntranetModelForm, IntranetForm
from intranet.widgets import DateTimePicker

from utils import duplicates, duplicate_list

from models import Prospect, Activity


class ImportForm(IntranetForm):
    file_data = forms.FileField(label=_(u'File source'))


class ProspectForm(IntranetModelForm):
    
    def __init__(self, *args, **kwargs):
        # We fetch the variable directly in the kwargs.
        # And delete it from the dict to make it available for super()
        self.check_duplicates = kwargs.pop('check_duplicates', False)
        super(ProspectForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = Prospect

    def clean(self):
        cleaned_data = self.cleaned_data
        if self.check_duplicates:

            # We only want to check for duplicates once.
            self.check_duplicates = False
            
            # Check for duplicates
            duplicate_result = duplicates(self.data)
            if duplicate_result:
                raise forms.ValidationError(_(u'This entry might be a duplicate. Check that it is not the same as one of the prospects listed below, which already exist in the database:%s') % duplicate_list(duplicate_result))
        return cleaned_data


class ActivityForm(IntranetModelForm):
    
    class Meta:
        model = Activity
        widgets = {
            'datetime': DateTimePicker(attrs={'placeholder': _(u'DD/MM/YYYY HH:MM')}),
            'duration': forms.TextInput(attrs={'placeholder': _(u'HH:MM:SS')}),
        }

