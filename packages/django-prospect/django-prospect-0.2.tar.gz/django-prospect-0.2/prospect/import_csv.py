# -*- coding: utf-8 -*-

import models, csv

def standardize(field_name, lang):
    ''' Read the given field name, and return the corresponding field name as defined in our model, or Null if the field name is unknown '''
    field_name = field_name.lower()
    if lang == 
    if field_name in {'raison sociale

def import_csv(src, lang='en'):
    reader = csv.reader(open(src, 'r'))
    if len(reader) == 0:
        raise csv.Error('The given CSV file is empty.')
    header = reader.next()
    # We replace the field names with standard names.
    header = [standardize(i, lang) for i in header]
    
    
    kwargs_list = []
    for row in reader:
        # Initialization of the kwargs
        kwargs = {
            'company_name': '',
            'field':        Null,
            'siret_code':   '',
            'title':        '',
            'first_name':   '',
            'last_name':    '',
            'profession':   '',
            'e_mail':       '',
            'phone_number': '',
            'street':       '',
            'postal_code':  '',
            'city':         '',
        }
        
        kwargs_list.append(kwargs)
    

'''
>>> import csv
>>> spamReader = csv.reader(open('eggs.csv', 'rb'), delimiter=' ', quotechar='|')
>>> for row in spamReader:
...     print ', '.join(row)
'''
