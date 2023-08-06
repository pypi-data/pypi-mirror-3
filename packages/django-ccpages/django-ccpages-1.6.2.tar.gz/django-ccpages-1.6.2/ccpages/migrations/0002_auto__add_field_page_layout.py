# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Page.layout'
        db.add_column('ccpages_page', 'layout',
                      self.gf('django.db.models.fields.FilePathField')(max_length=100, path='/Users/jcurle/Sites/mph/mph/mph//templates/ccpages/layouts/', null=True, match='[\\w\\.\\-]+\\.html', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Page.layout'
        db.delete_column('ccpages_page', 'layout')


    models = {
        'ccpages.page': {
            'Meta': {'ordering': "['order']", 'object_name': 'Page'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_rendered': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layout': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'path': "'/Users/jcurle/Sites/mph/mph/mph//templates/ccpages/layouts/'", 'null': 'True', 'match': "'[\\\\w\\\\.\\\\-]+\\\\.html'", 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.DecimalField', [], {'default': '10.0', 'max_digits': '8', 'decimal_places': '2'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['ccpages.Page']"}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'ccpages.pageattachment': {
            'Meta': {'object_name': 'PageAttachment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.DecimalField', [], {'default': '10.0', 'max_digits': '8', 'decimal_places': '2'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ccpages.Page']"}),
            'src': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'ccpages.pageimage': {
            'Meta': {'object_name': 'PageImage'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.DecimalField', [], {'default': '10.0', 'max_digits': '8', 'decimal_places': '2'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ccpages.Page']"}),
            'src': ('ccthumbs.fields.ImageWithThumbsField', [], {'blank': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ccpages']