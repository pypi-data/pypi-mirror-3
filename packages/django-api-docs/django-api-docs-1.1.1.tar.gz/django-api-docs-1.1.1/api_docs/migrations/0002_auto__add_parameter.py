# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Parameter'
        db.create_table('api_docs_parameter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('var_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('api_docs', ['Parameter'])

        # Adding M2M table for field parameter on 'APIMethod'
        db.create_table('api_docs_apimethod_parameter', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('apimethod', models.ForeignKey(orm['api_docs.apimethod'], null=False)),
            ('parameter', models.ForeignKey(orm['api_docs.parameter'], null=False))
        ))
        db.create_unique('api_docs_apimethod_parameter', ['apimethod_id', 'parameter_id'])


    def backwards(self, orm):
        
        # Deleting model 'Parameter'
        db.delete_table('api_docs_parameter')

        # Removing M2M table for field parameter on 'APIMethod'
        db.delete_table('api_docs_apimethod_parameter')


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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'var_type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['api_docs']
