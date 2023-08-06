# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'PostVersion.post'
        db.alter_column('omblog_postversion', 'post_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['omblog.Post'], null=True))
    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'PostVersion.post'
        raise RuntimeError("Cannot reverse this migration. 'PostVersion.post' and its values cannot be restored.")
    models = {
        'omblog.post': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Post'},
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rendered_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'source_content': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['omblog.Tag']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'omblog.postversion': {
            'Meta': {'ordering': "['-created']", 'object_name': 'PostVersion'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance': ('picklefield.fields.PickledObjectField', [], {}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omblog.Post']", 'null': 'True', 'blank': 'True'})
        },
        'omblog.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['omblog']