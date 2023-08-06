# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Prospect.surname'
        db.delete_column('prospect_prospect', 'surname')

        # Deleting field 'Prospect.address'
        db.delete_column('prospect_prospect', 'address')

        # Deleting field 'Prospect.town'
        db.delete_column('prospect_prospect', 'town')

        # Adding field 'Prospect.last_name'
        db.add_column('prospect_prospect', 'last_name',
                      self.gf('django.db.models.fields.CharField')(default='Smith', max_length=50),
                      keep_default=False)

        # Adding field 'Prospect.street'
        db.add_column('prospect_prospect', 'street',
                      self.gf('django.db.models.fields.CharField')(default='2 rue des arbres', max_length=100),
                      keep_default=False)

        # Adding field 'Prospect.city'
        db.add_column('prospect_prospect', 'city',
                      self.gf('django.db.models.fields.CharField')(default='new york', max_length=50),
                      keep_default=False)

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Prospect.surname'
        raise RuntimeError("Cannot reverse this migration. 'Prospect.surname' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Prospect.address'
        raise RuntimeError("Cannot reverse this migration. 'Prospect.address' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Prospect.town'
        raise RuntimeError("Cannot reverse this migration. 'Prospect.town' and its values cannot be restored.")
        # Deleting field 'Prospect.last_name'
        db.delete_column('prospect_prospect', 'last_name')

        # Deleting field 'Prospect.street'
        db.delete_column('prospect_prospect', 'street')

        # Deleting field 'Prospect.city'
        db.delete_column('prospect_prospect', 'city')

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
            'siret_number': ('django.db.models.fields.CharField', [], {'max_length': '14'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        }
    }

    complete_apps = ['prospect']