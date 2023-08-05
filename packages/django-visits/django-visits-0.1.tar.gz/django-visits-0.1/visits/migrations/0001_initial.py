# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Visit'
        db.create_table('counter_visit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page_visited', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('visitor_ip', self.gf('django.db.models.fields.IPAddressField')(db_index=True, max_length=15, null=True, blank=True)),
            ('last_visit', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('visits', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('blocked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('counter', ['Visit'])


    def backwards(self, orm):
        
        # Deleting model 'Visit'
        db.delete_table('counter_visit')


    models = {
        'counter.visit': {
            'Meta': {'object_name': 'Visit'},
            'blocked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_visit': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'page_visited': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'visitor_ip': ('django.db.models.fields.IPAddressField', [], {'db_index': 'True', 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'visits': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['counter']
