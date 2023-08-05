# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Parameter.get_or_url'
        db.add_column('api_docs_parameter', 'get_or_url', self.gf('django.db.models.fields.CharField')(default='url', max_length=20), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Parameter.get_or_url'
        db.delete_column('api_docs_parameter', 'get_or_url')


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
            'parameter': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['api_docs.Parameter']", 'symmetrical': 'False', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'api_docs.apiobject': {
            'Meta': {'object_name': 'APIObject'},
            'api_doc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api_docs.APIDoc']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'api_docs.parameter': {
            'Meta': {'object_name': 'Parameter'},
            'default_value': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'get_or_url': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'var_type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['api_docs']
