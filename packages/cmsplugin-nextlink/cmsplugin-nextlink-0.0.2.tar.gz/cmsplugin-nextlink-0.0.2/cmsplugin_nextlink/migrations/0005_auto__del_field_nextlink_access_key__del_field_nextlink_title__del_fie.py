# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'NextLink.access_key'
        db.delete_column('cmsplugin_nextlink', 'access_key')

        # Deleting field 'NextLink.title'
        db.delete_column('cmsplugin_nextlink', 'title')

        # Deleting field 'NextLink.url'
        db.delete_column('cmsplugin_nextlink', 'url')

        # Deleting field 'NextLink.alt_attribute'
        db.delete_column('cmsplugin_nextlink', 'alt_attribute')

        # Adding field 'NextLink.link_url'
        db.add_column('cmsplugin_nextlink', 'link_url', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.mailto_address'
        db.add_column('cmsplugin_nextlink', 'mailto_address', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.mailto_subject'
        db.add_column('cmsplugin_nextlink', 'mailto_subject', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.link_attr_title'
        db.add_column('cmsplugin_nextlink', 'link_attr_title', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.link_attr_accesskey'
        db.add_column('cmsplugin_nextlink', 'link_attr_accesskey', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.link_attr_tabindex'
        db.add_column('cmsplugin_nextlink', 'link_attr_tabindex', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.link_attr_class'
        db.add_column('cmsplugin_nextlink', 'link_attr_class', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.link_attr_id'
        db.add_column('cmsplugin_nextlink', 'link_attr_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.link_attr_dir'
        db.add_column('cmsplugin_nextlink', 'link_attr_dir', self.gf('django.db.models.fields.CharField')(default='rtl', max_length=256, null=True), keep_default=False)

        # Adding field 'NextLink.link_attr_style'
        db.add_column('cmsplugin_nextlink', 'link_attr_style', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.link_attr_name'
        db.add_column('cmsplugin_nextlink', 'link_attr_name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.link_attr_charset'
        db.add_column('cmsplugin_nextlink', 'link_attr_charset', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.image_attr_alt'
        db.add_column('cmsplugin_nextlink', 'image_attr_alt', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Changing field 'NextLink.protocol'
        db.alter_column('cmsplugin_nextlink', 'protocol', self.gf('django.db.models.fields.CharField')(max_length=8))


    def backwards(self, orm):
        
        # Adding field 'NextLink.access_key'
        db.add_column('cmsplugin_nextlink', 'access_key', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.title'
        db.add_column('cmsplugin_nextlink', 'title', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Adding field 'NextLink.url'
        db.add_column('cmsplugin_nextlink', 'url', self.gf('django.db.models.fields.CharField')(default=False, max_length=256), keep_default=False)

        # Adding field 'NextLink.alt_attribute'
        db.add_column('cmsplugin_nextlink', 'alt_attribute', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Deleting field 'NextLink.link_url'
        db.delete_column('cmsplugin_nextlink', 'link_url')

        # Deleting field 'NextLink.mailto_address'
        db.delete_column('cmsplugin_nextlink', 'mailto_address')

        # Deleting field 'NextLink.mailto_subject'
        db.delete_column('cmsplugin_nextlink', 'mailto_subject')

        # Deleting field 'NextLink.link_attr_title'
        db.delete_column('cmsplugin_nextlink', 'link_attr_title')

        # Deleting field 'NextLink.link_attr_accesskey'
        db.delete_column('cmsplugin_nextlink', 'link_attr_accesskey')

        # Deleting field 'NextLink.link_attr_tabindex'
        db.delete_column('cmsplugin_nextlink', 'link_attr_tabindex')

        # Deleting field 'NextLink.link_attr_class'
        db.delete_column('cmsplugin_nextlink', 'link_attr_class')

        # Deleting field 'NextLink.link_attr_id'
        db.delete_column('cmsplugin_nextlink', 'link_attr_id')

        # Deleting field 'NextLink.link_attr_dir'
        db.delete_column('cmsplugin_nextlink', 'link_attr_dir')

        # Deleting field 'NextLink.link_attr_style'
        db.delete_column('cmsplugin_nextlink', 'link_attr_style')

        # Deleting field 'NextLink.link_attr_name'
        db.delete_column('cmsplugin_nextlink', 'link_attr_name')

        # Deleting field 'NextLink.link_attr_charset'
        db.delete_column('cmsplugin_nextlink', 'link_attr_charset')

        # Deleting field 'NextLink.image_attr_alt'
        db.delete_column('cmsplugin_nextlink', 'image_attr_alt')

        # Changing field 'NextLink.protocol'
        db.alter_column('cmsplugin_nextlink', 'protocol', self.gf('django.db.models.fields.CharField')(max_length=8, null=True))


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
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_attr_alt': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'link_attr_accesskey': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'link_attr_charset': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'link_attr_class': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'link_attr_dir': ('django.db.models.fields.CharField', [], {'default': "'rtl'", 'max_length': '256', 'null': 'True'}),
            'link_attr_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'link_attr_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'link_attr_style': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'link_attr_tabindex': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'link_attr_title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'link_created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'link_expired': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(3011, 11, 25, 16, 48, 21, 79764)', 'blank': 'True'}),
            'link_url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'mailto_address': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'mailto_subject': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'protocol': ('django.db.models.fields.CharField', [], {'default': "'internal'", 'max_length': '8'})
        }
    }

    complete_apps = ['cmsplugin_nextlink']
