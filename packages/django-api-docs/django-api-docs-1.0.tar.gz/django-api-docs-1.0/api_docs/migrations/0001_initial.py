# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'APIDoc'
        db.create_table('api_docs_apidoc', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('api_docs', ['APIDoc'])

        # Adding model 'APIObject'
        db.create_table('api_docs_apiobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('api_doc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api_docs.APIDoc'])),
        ))
        db.send_create_signal('api_docs', ['APIObject'])

        # Adding model 'APIMethod'
        db.create_table('api_docs_apimethod', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('api_object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api_docs.APIObject'])),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('short_description', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('api_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('api_docs', ['APIMethod'])


    def backwards(self, orm):
        
        # Deleting model 'APIDoc'
        db.delete_table('api_docs_apidoc')

        # Deleting model 'APIObject'
        db.delete_table('api_docs_apiobject')

        # Deleting model 'APIMethod'
        db.delete_table('api_docs_apimethod')


    models = {
        'api_docs.apidoc': {
            'Meta': {'object_name': 'APIDoc'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'api_docs.apimethod': {
            'Meta': {'object_name': 'APIMethod'},
            'api_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api_docs.APIObject']"}),
            'api_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'short_description': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'api_docs.apiobject': {
            'Meta': {'object_name': 'APIObject'},
            'api_doc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api_docs.APIDoc']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['api_docs']
