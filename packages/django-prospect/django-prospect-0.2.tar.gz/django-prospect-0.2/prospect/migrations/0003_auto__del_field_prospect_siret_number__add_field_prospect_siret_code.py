# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Prospect.siret_number'
        db.delete_column('prospect_prospect', 'siret_number')

        # Adding field 'Prospect.siret_code'
        db.add_column('prospect_prospect', 'siret_code',
                      self.gf('django.db.models.fields.CharField')(default='01234567890123', max_length=14),
                      keep_default=False)

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Prospect.siret_number'
        raise RuntimeError("Cannot reverse this migration. 'Prospect.siret_number' and its values cannot be restored.")
        # Deleting field 'Prospect.siret_code'
        db.delete_column('prospect_prospect', 'siret_code')

    models = {
        'prospect.field': {
            'Meta': {'ordering': "['name']", 'object_name': 'Field'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'prospect.prospect': {
            'Meta': {'ordering': "['company_name']", 'object_name': 'Prospect'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'e_mail': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prospects'", 'to': "orm['prospect.Field']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'profession': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'siret_code': ('django.db.models.fields.CharField', [], {'max_length': '14'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        }
    }

    complete_apps = ['prospect']