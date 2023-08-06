# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'TwitterStatus', fields ['created_date']
        db.create_index('twittersync_twitterstatus', ['created_date'])

    def backwards(self, orm):
        
        # Removing index on 'TwitterStatus', fields ['created_date']
        db.delete_index('twittersync_twitterstatus', ['created_date'])


    models = {
        'twittersync.twitteraccount': {
            'Meta': {'ordering': "('screen_name',)", 'object_name': 'TwitterAccount'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'screen_name': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'twittersync.twitterstatus': {
            'Meta': {'ordering': "('-created_date',)", 'object_name': 'TwitterStatus'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tweets'", 'to': "orm['twittersync.TwitterAccount']"}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status_id': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['twittersync']
