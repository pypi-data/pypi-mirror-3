# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'FAQEntry.answer'
        db.alter_column('cmsplugin_multiple_faq_faqentry', 'answer', self.gf('django.db.models.fields.TextField')())


    def backwards(self, orm):
        
        # Changing field 'FAQEntry.answer'
        db.alter_column('cmsplugin_multiple_faq_faqentry', 'answer', self.gf('django.db.models.fields.CharField')(max_length=128))


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
        'cmsplugin_multiple_faq.faqentry': {
            'Meta': {'object_name': 'FAQEntry'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            'faq_list': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'faq_entries'", 'to': "orm['cmsplugin_multiple_faq.FAQList']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'cmsplugin_multiple_faq.faqlist': {
            'Meta': {'object_name': 'FAQList'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'cmsplugin_multiple_faq.faqplugin': {
            'Meta': {'object_name': 'FAQPlugin', 'db_table': "'cmsplugin_faqplugin'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'faq_list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cmsplugin_multiple_faq.FAQList']"})
        }
    }

    complete_apps = ['cmsplugin_multiple_faq']
