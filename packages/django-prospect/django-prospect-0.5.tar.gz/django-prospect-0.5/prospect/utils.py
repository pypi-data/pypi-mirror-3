# -*- coding: utf-8 -*-

import uuid
import os
import re

from django.conf import settings
from django.db.models import Q
from django.forms import models
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from intranet.base_forms import IntranetModelForm

from models import Prospect, Field


def _get_unicode(obj):
    if not isinstance(obj, unicode):
        return unicode(str(obj), encoding='utf-8')
    else:
        return obj

def standardize(field_name, lang):
    '''
    Read the given field name, and return the corresponding field name as defined in our model, or None if the field name is unknown
    '''

    field_name = _get_unicode(field_name)
    field_name = field_name.lower().strip()
    standard_field_name = None
    error = None
    field_name_error = _(u'No field name could be associated with "<b>%s</b>". So the corresponding entries could not be imported.') % escape(field_name)

    if lang == 'en':
        if field_name in {u'company name', u'company', u'name'}:
            standard_field_name = u'company_name'
        elif field_name in {u'field'}:
            standard_field_name = u'field'
        elif field_name in {u'siret code', u'siret number'}:
            standard_field_name = u'siret_code'
        elif field_name in {u'title'}:
            standard_field_name = u'title'
        elif field_name in {u'first name'}:
            standard_field_name = u'first_name'
        elif field_name in {u'last name', u'surname'}:
            standard_field_name = u'last_name'
        elif field_name in {u'profession'}:
            standard_field_name = u'profession'
        elif field_name in {u'email', u'e-mail', u'email address', u'e-mail address'}:
            standard_field_name = u'e_mail'
        elif field_name in {u'telephone', u'telephone number', u'phone', u'phone number'}:
            standard_field_name = u'phone_number'
        elif field_name in {u'street', u'addresse'}:
            standard_field_name = u'street'
        elif field_name in {u'postal code', u'zip code', u'zip'}:
            standard_field_name = u'postal_code'
        elif field_name in {u'town', u'city'}:
            standard_field_name = u'city'
        else:
            error = field_name_error
    elif lang == 'fr':
        if field_name in {u'raison sociale'}:
            standard_field_name = u'company_name'
        elif field_name in {u'domaine', u'categorie', u'catégorie', u'secteur d\'activité', u'secteur d\'activite'}:
            standard_field_name = u'field'
        elif field_name in {u'code siret', u'numéro siret', u'numero siret'}:
            standard_field_name = u'siret_code'
        elif field_name in {u'civilite', u'civilité', u'titre'}:
            standard_field_name = u'title'
        elif field_name in {u'prénom', u'prenom'}:
            standard_field_name = u'first_name'
        elif field_name in {u'nom'}:
            standard_field_name = u'last_name'
        elif field_name in {u'profession', u'fonction'}:
            standard_field_name = u'profession'
        elif field_name in {u'email', u'e-mail', u'adresse email', u'adresse e-mail'}:
            standard_field_name = u'e_mail'
        elif field_name in {u'telephone', u'téléphone', u'numero de telephone', u'numéro de téléphone'}:
            standard_field_name = u'phone_number'
        elif field_name in {u'rue', u'adresse'}:
            standard_field_name = u'street'
        elif field_name in {u'code postal'}:
            standard_field_name = u'postal_code'
        elif field_name in {u'ville', u'commune'}:
            standard_field_name = u'city'
        else:
            error = field_name_error
    else:
        error = _(u'The language "<b>%s</b>" is not supported.') % escape(lang)
    return (standard_field_name, error)


def duplicates(data):
    # If at least a part of the name is defined
    if data['first_name'] or data['last_name']:
        return Prospect.objects.filter(
            Q(company_name = data['company_name']) |
            Q(first_name = data['first_name'], last_name = data['last_name'])
        )
    else:
        return Prospect.objects.filter(company_name = data['company_name'])


def duplicate_list(duplicate_result):
    duplicate_list = u''
    for prospect in duplicate_result:
        duplicate_list += u'<li>'
        if prospect.first_name or prospect.last_name:
            # Translators: [Name of a person (first name and last name)] AT [name of a company]
            duplicate_list += u'<b>%s %s</b> %s ' % (escape(prospect.first_name), escape(prospect.last_name), _(u'at'))
        duplicate_list += u'<b>%s</b></li>' % escape(prospect.company_name)
    return '<ul>%s</ul>' % duplicate_list


def _treat(header, row, row_num, ignore_duplicates = False, prompt_me = False):
    '''
    Try to insert a new entry in the database with the values given in the string list `row`, in the order given by the string list `header`. Returns an error as a string (that can be empty)
    '''
    # Initialization of the kwargs
    kwargs = {
        'company_name': '',
        'field'       : None,
        'siret_code'  : '',
        'title'       : '',
        'first_name'  : '',
        'last_name'   : '',
        'profession'  : '',
        'e_mail'      : '',
        'phone_number': '',
        'street'      : '',
        'postal_code' : '',
        'city'        : '',
    }
    
    error = u''
    
    # Filling of the kwargs
    for (field_name, value) in zip(header, row):
        # The None field names correspond to unknown fields so we skip them.
        if field_name != None:
            value = _get_unicode(value)
            # Cleaning the value
            value = value.strip()
            if field_name == u'field':
                if value:
                    try:
                        kwargs[field_name] = Field.objects.get(name = value).id
                    except Exception:
                        error = _(u'The field "<b>%s</b>" does not exist in the database. You should first create it.') % escape(value)
            else:
                kwargs[field_name] = value
    
    duplicate_result = []
    if prompt_me or ignore_duplicates:
        # Check if the prospect does not already exist in the database
        duplicate_result = duplicates(kwargs)
    if prompt_me and duplicate_result:
        error = _(u'This entry was detected as a possible duplicate. Check that it is not the same as one of the prospects listed below, which already exist in the database:%s') % duplicate_list(duplicate_result)
    # Check if the row has the same length as the header
    elif len(row) != len(header):
        error = _(u'The row #%d in your data had a different length from the header.') % row_num
    
    # Create a form filled with the kwargs.
    form_class = models.modelform_factory(Prospect, IntranetModelForm)
    form = form_class(kwargs)
    
    # Check if the kwargs are valid.
    # Else return (explicit) error.
    if form.is_valid() and not error:
        ignored = ignore_duplicates and duplicate_result
        if not ignored:
            Prospect.objects.create(**form.cleaned_data)
        return (None, ignored)
    else:
        return ((error, form.data), False)


def import_csv(src, lang, ignore_duplicates = False, prompt_me = False):
    '''
    Import the CSV file from a source path and insert valid prospects found in the list into the database
    '''
    import csv
    reader = csv.reader(open(src, 'r'))
    
    general_errors = []
    # This is a list of couples (error, form to modify)
    particular_results = []
    try:
        header = reader.next()
    except StopIteration:
        # This error should never happen because the FileField already checks if the file is empty, but just in case...
        general_errors.append(_('The given CSV file seems to be empty.'))
        return (general_errors, ())
    
    # We replace the field names with standard names.
    standardized_header = []
    for field_name in header:
        (field_name, error) = standardize(field_name, lang)
        standardized_header.append(field_name)
        if error:
            general_errors.append(error)
    header = standardized_header
    del standardized_header
    
    nb_inserted = 0
    nb_ignored = 0
    for row in reader:
        (result, ignored) = _treat(header, row, reader.line_num, ignore_duplicates, prompt_me)
        if ignored:
            nb_ignored += 1
        elif not result:
            nb_inserted += 1
        if result:
            particular_results.append(result)
    
    # reverse so that we correct the entries in the same order as in the original file
    particular_results.reverse()
    return (nb_inserted, nb_ignored, general_errors, particular_results)


def import_xls(src, lang, ignore_duplicates = False, prompt_me = False):
    '''
    Import an XLS file from a source path and insert valid prospects found in the list into the database
    '''
    import xlrd
    book = xlrd.open_workbook(src)
    
    general_errors = []
    # This is a list of couples (error, form to modify)
    particular_results = []
    
    nb_inserted = 0
    nb_ignored = 0
    for sheet in book.sheets():
        try:
            header = [field_name.value for field_name in sheet.row(0)]
            # We replace the field names with standard names.
            standardized_header = []
            for field_name in header:
                (field_name, error) = standardize(field_name, lang)
                standardized_header.append(field_name)
                if error:
                    general_errors.append(error)
            header = standardized_header
            del standardized_header
            
            for row_num in xrange(1, sheet.nrows):
                row = [cell.value for cell in sheet.row(row_num)]
                (result, ignored) = _treat(header, row, row_num, ignore_duplicates, prompt_me)
                if ignored:
                    nb_ignored += 1
                elif not result:
                    nb_inserted += 1
                if result:
                    particular_results.append(result)
            
        except IndexError:
            general_errors.append(_('The XLS sheet "<b>%s</b>" seems to be empty.') % escape(sheet.name))
    
    # Reverse so that we correct the entries in the same order as in the original file
    particular_results.reverse()
    return (nb_inserted, nb_ignored, general_errors, particular_results)


def import_file(src, lang='en', ignore_duplicates = False, prompt_me = False):
    '''
    Import a file from a source path and insert valid prospects found in the list into the database.
    If ignore_duplicates is true, we don't insert the entries whose company name, or first and last name is found in the database.
    If prompt_me is true, we prompt the user with a form everytime a duplicte is detected.
    '''
    if re.match(r'.*\.csv$', src):
        return import_csv(src, lang, ignore_duplicates, prompt_me)
    elif re.match(r'.*\.xls$', src):
        return import_xls(src, lang, ignore_duplicates, prompt_me)
    else:
        return None


def handler_save_tmp_file(file_obj):
    tmp_filename = u'%s-%s' % (uuid.uuid4(), file_obj.name)
    path = os.path.join(settings.FILE_UPLOAD_TEMP_DIR or '/tmp', tmp_filename)
    destination = open(path, 'wb+')
    for chunk in file_obj.chunks():
        destination.write(chunk)
    destination.close()
    return path
