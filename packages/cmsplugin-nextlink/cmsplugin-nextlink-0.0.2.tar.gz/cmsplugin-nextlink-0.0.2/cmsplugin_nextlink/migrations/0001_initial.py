# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'NextLink'
        db.create_table('cmsplugin_nextlink', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('protocol', self.gf('django.db.models.fields.CharField')(default='internal', max_length=8, null=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('access_key', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('link_create', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('link_expired', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(3011, 11, 3, 8, 46, 3, 102724), blank=True)),
        ))
        db.send_create_signal('cmsplugin_nextlink', ['NextLink'])


    def backwards(self, orm):
        
        # Deleting model 'NextLink'
        db.delete_table('cmsplugin_nextlink')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'cmsplugin_nextlink.nextlink': {
            'Meta': {'object_name': 'NextLink', 'db_table': "'cmsplugin_nextlink'", '_ormbases': ['cms.CMSPlugin']},
            'access_key': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'link_create': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'link_expired': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(3011, 11, 3, 8, 46, 3, 102724)', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'protocol': ('django.db.models.fields.CharField', [], {'default': "'internal'", 'max_length': '8', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['cmsplugin_nextlink']
