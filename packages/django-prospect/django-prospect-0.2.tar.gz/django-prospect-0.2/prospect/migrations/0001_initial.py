# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Field'
        db.create_table('prospect_field', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('prospect', ['Field'])

        # Adding model 'Prospect'
        db.create_table('prospect_prospect', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('profession', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('town', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('e_mail', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('siret_number', self.gf('django.db.models.fields.CharField')(max_length=14)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['prospect.Field'])),
        ))
        db.send_create_signal('prospect', ['Prospect'])

    def backwards(self, orm):
        # Deleting model 'Field'
        db.delete_table('prospect_field')

        # Deleting model 'Prospect'
        db.delete_table('prospect_prospect')

    models = {
        'prospect.field': {
            'Meta': {'ordering': "['name']", 'object_name': 'Field'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'prospect.prospect': {
            'Meta': {'ordering': "['company_name']", 'object_name': 'Prospect'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'e_mail': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['prospect.Field']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'profession': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'siret_number': ('django.db.models.fields.CharField', [], {'max_length': '14'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'town': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['prospect']