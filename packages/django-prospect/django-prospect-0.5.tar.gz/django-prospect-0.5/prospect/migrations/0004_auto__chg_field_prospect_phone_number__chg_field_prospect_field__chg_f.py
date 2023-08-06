# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Prospect.phone_number'
        db.alter_column('prospect_prospect', 'phone_number', self.gf('intranet.widgets.PhoneField')(max_length=16))

        # Changing field 'Prospect.field'
        db.alter_column('prospect_prospect', 'field_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['prospect.Field']))

        # Changing field 'Prospect.siret_code'
        db.alter_column('prospect_prospect', 'siret_code', self.gf('intranet.widgets.SiretField')(max_length=14))
    def backwards(self, orm):

        # Changing field 'Prospect.phone_number'
        db.alter_column('prospect_prospect', 'phone_number', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Changing field 'Prospect.field'
        db.alter_column('prospect_prospect', 'field_id', self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['prospect.Field']))

        # Changing field 'Prospect.siret_code'
        db.alter_column('prospect_prospect', 'siret_code', self.gf('django.db.models.fields.CharField')(max_length=14))
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
            'e_mail': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'prospects'", 'null': 'True', 'to': "orm['prospect.Field']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'phone_number': ('intranet.widgets.PhoneField', [], {'max_length': '16', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'profession': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'siret_code': ('intranet.widgets.SiretField', [], {'max_length': '14', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
        }
    }

    complete_apps = ['prospect']