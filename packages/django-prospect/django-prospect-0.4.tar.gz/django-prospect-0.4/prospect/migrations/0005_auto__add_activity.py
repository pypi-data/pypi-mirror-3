# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Activity'
        db.create_table('prospect_activity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(related_name='activity', to=orm['prospect.Prospect'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('duration', self.gf('django.db.models.fields.TimeField')(blank=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('is_important', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('direction', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('activity_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('prospect', ['Activity'])

    def backwards(self, orm):
        # Deleting model 'Activity'
        db.delete_table('prospect_activity')

    models = {
        'prospect.activity': {
            'Meta': {'ordering': "['-datetime']", 'object_name': 'Activity'},
            'activity_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activity'", 'to': "orm['prospect.Prospect']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'duration': ('django.db.models.fields.TimeField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_important': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
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