# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'NextLink.link_create'
        db.delete_column('cmsplugin_nextlink', 'link_create')

        # Adding field 'NextLink.link_created'
        db.add_column('cmsplugin_nextlink', 'link_created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2012, 7, 4, 13, 27, 52, 84098), blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'NextLink.link_create'
        db.add_column('cmsplugin_nextlink', 'link_create', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2012, 7, 4, 13, 27, 42, 300238), blank=True), keep_default=False)

        # Deleting field 'NextLink.link_created'
        db.delete_column('cmsplugin_nextlink', 'link_created')


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
            'alt_attribute': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'link_created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'link_expired': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(3011, 11, 5, 13, 27, 28, 121243)', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'protocol': ('django.db.models.fields.CharField', [], {'default': "'internal'", 'max_length': '8', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['cmsplugin_nextlink']
