# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.forms import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required

from intranet.base_views import IntranetListView, IntranetCreateView, IntranetUpdateView
from intranet.base_forms import IntranetModelForm

from prospect.utils import import_file, handler_save_tmp_file
from prospect.forms import ImportForm, ProspectForm, ActivityForm

from models import Prospect, Activity


class FieldListView(IntranetListView):
    search_fields = ('name', )


class ProspectListView(IntranetListView):
    list_display = ('company_name', 'first_name', 'last_name', 'field_display')
    list_display_links = ('company_name')
    search_fields = (
        'company_name',
        'first_name',
        'last_name',
        'field__name',
        'profession',
        'city',
    )

@login_required
def treat_correction(request, cancel = False, skip = False):
    if cancel:
        # Cancel all the rest
        del request.session['import_result']
        del request.session['import_stats']
        return redirect('prospect-list')
    elif skip:
        # Skip this one
        (general_errors, particular_results) = request.session['import_result']
        particular_results.pop()
        request.session['import_stats']['nb_cancelled'] += 1
        if particular_results:
            request.session['import_result'] = (general_errors, particular_results)
        else:
            # We just skipped the last form.
            # Until now, the general errors were displayed above every correction form. Now we only want to display a success message so we delete the general errors.
            request.session['import_result'] = ([], [])
        return _import_result(request)
    else:
        # Submit the form
        form_class = models.modelform_factory(Prospect, IntranetModelForm)
        form = form_class(request.POST)
        (general_errors, particular_results) = request.session['import_result']
        if form.is_valid():
            Prospect.objects.create(**form.cleaned_data)
            request.session['import_stats']['nb_edited'] += 1
            particular_results.pop()
            if particular_results:
                # We tell the Django the session variables have been modified, so that it saves the new data.
                request.session.modified = True
            else:
                # We just corrected the last form.
                # Until now, the general errors were displayed above every correction form. Now we only want to display a success message so we delete the general errors.
                request.session['import_result'] = ([], [])
        else:
            # Replace the data and errors of the current form with the newly inserted data.
            (particular_error, form_data) = particular_results.pop()
            particular_results.append((particular_error, form.data))
            # We tell the Django the session variables have been modified, so that it saves the new data.
            request.session.modified = True
        return _import_result(request)

@login_required
def _import_result(request):
    (general_errors, particular_results) = request.session['import_result']
    if particular_results:
        # Errors in some entries (+ general errors)
        nb_forms_to_edit = len(particular_results)
        (particular_error, form_data) = particular_results[-1]
        
        form_class = models.modelform_factory(Prospect, IntranetModelForm)
        form_to_edit = form_class(form_data)

        return render_to_response(
            'prospect/prospect/import_result.html',
            {
                'general_errors': general_errors,
                'exist_field_errors': True,
                'particular_error': particular_error,
                'form_to_edit': form_to_edit,
                'nb_forms_to_edit': nb_forms_to_edit,
            },
            context_instance = RequestContext(request)
        )
    else:
        # Either:
        # Only general errors. Then you can just click 'OK'.
        # After displaying this page, we don't need the import result anymore.
        
        # Or:
        # Successful import
        
        nb_auto_inserted = request.session['import_stats']['nb_auto_inserted']
        nb_edited =        request.session['import_stats']['nb_edited']
        nb_cancelled =     request.session['import_stats']['nb_cancelled']
        nb_ignored =       request.session['import_stats']['nb_ignored']
        del request.session['import_result']
        del request.session['import_stats']
        return render_to_response(
            'prospect/prospect/import_result.html',
            {
                'exist_field_errors': False,
                'nb_auto_inserted'  : nb_auto_inserted,
                'nb_edited'         : nb_edited,
                'nb_cancelled'      : nb_cancelled,
                'nb_ignored'        : nb_ignored,
            },
            context_instance = RequestContext(request)
        )

@login_required
def import_index(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            file_data = form.cleaned_data['file_data']
            path = handler_save_tmp_file(file_data)
            result = import_file(
                path,
                lang = request.POST['lang'],
                ignore_duplicates = request.POST['mode'] == 'ignore_duplicates',
                prompt_me = request.POST['mode'] == 'prompt_me',
            )
            # We don't need the file anymore.
            os.remove(path)
            if result:
                (nb_inserted, nb_ignored, general_errors, particular_results) = result
                request.session['import_result'] = (general_errors, particular_results)
                request.session['import_stats'] = {
                    'nb_auto_inserted'  : nb_inserted,
                    'nb_edited'         : 0,
                    'nb_cancelled'      : 0,
                    'nb_ignored'        : nb_ignored,
                }
                return _import_result(request)
            else:
                # File format not supported
                return render_to_response(
                    'prospect/prospect/import.html',
                    {'form': form, 'file_error': _(u'File format not supported')},
                    context_instance = RequestContext(request)
                )
        else:
            return render_to_response(
                'prospect/prospect/import.html',
                {'form': form},
                context_instance = RequestContext(request)
            )
    else:
        form = ImportForm()
        return render_to_response(
            'prospect/prospect/import.html',
            {'form': form},
            context_instance = RequestContext(request)
        )


class ProspectCreateView(IntranetCreateView):
    form_class = ProspectForm
    
    def get_form_kwargs(self, **kwargs):
        
        # We fetch the parents' kwargs.
        kwargs = super(ProspectCreateView, self).get_form_kwargs(**kwargs)
        
        # The variable check_duplicates is given by the POST hidden field if it exists, else it is true.
        # We add the variable directly in the kwargs.
        try:
            # Cast the variable as an integer.
            post_value = int(self.request.POST.get('check_duplicates', '1'))
        except ValueError:
            post_value = 1
        kwargs['check_duplicates'] = bool(post_value)

        return kwargs


class ActivityCreateView(IntranetCreateView):
    form_class = ActivityForm
    
    def get_form_kwargs(self, **kwargs):
        kwargs = super(ActivityCreateView, self).get_form_kwargs(**kwargs)
        kwargs['initial']['contact'] = self.request.GET.get('contact')
        return kwargs


class ActivityUpdateView(IntranetUpdateView):
    form_class = ActivityForm


class ActivityListView(IntranetListView):
    list_display = ('is_important_display', 'datetime_display', 'contact', 'subject', 'activity_type_display', 'direction_display', 'duration_display', 'comments_display')
    list_display_links = ('subject')
    search_fields = (
        'subject',
        'comments',
    )
    list_filter = (
        'is_important',
    )


class ProspectActivityView(ActivityListView):
    
    list_display = ('is_important_display', 'datetime_display', 'subject', 'activity_type_display', 'direction_display', 'duration_display', 'comments_display')
    model = Activity
    
    def get_context_data(self, **kwargs):
        context_data = super(ProspectActivityView, self).get_context_data(**kwargs)
        context_data['prospect'] = Prospect.objects.get(pk=self.kwargs['prospect_id'])
        return context_data
    
    def get_queryset(self):
        queryset = super(ProspectActivityView, self).get_queryset()
        return queryset.filter(contact_id=self.kwargs['prospect_id'])

