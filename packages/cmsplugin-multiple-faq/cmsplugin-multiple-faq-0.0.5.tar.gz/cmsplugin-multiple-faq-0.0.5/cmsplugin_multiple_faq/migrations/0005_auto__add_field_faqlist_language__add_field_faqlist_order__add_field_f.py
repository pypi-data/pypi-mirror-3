# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'FAQList.language'
        db.add_column('cmsplugin_multiple_faq_faqlist', 'language', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True), keep_default=False)

        # Adding field 'FAQList.order'
        db.add_column('cmsplugin_multiple_faq_faqlist', 'order', self.gf('django.db.models.fields.IntegerField')(default=100), keep_default=False)

        # Adding field 'FAQEntry.order'
        db.add_column('cmsplugin_multiple_faq_faqentry', 'order', self.gf('django.db.models.fields.IntegerField')(default=100), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'FAQList.language'
        db.delete_column('cmsplugin_multiple_faq_faqlist', 'language')

        # Deleting field 'FAQList.order'
        db.delete_column('cmsplugin_multiple_faq_faqlist', 'order')

        # Deleting field 'FAQEntry.order'
        db.delete_column('cmsplugin_multiple_faq_faqentry', 'order')


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
            'Meta': {'ordering': "['order', 'question']", 'object_name': 'FAQEntry'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            'faq_list': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'faq_entries'", 'to': "orm['cmsplugin_multiple_faq.FAQList']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'question': ('django.db.models.fields.TextField', [], {})
        },
        'cmsplugin_multiple_faq.faqlist': {
            'Meta': {'ordering': "['order', 'title']", 'object_name': 'FAQList'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'cmsplugin_multiple_faq.faqlistplugin': {
            'Meta': {'object_name': 'FAQListPlugin', 'db_table': "'cmsplugin_faqlistplugin'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'faq_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cmsplugin_multiple_faq.FAQList']", 'symmetrical': 'False'})
        },
        'cmsplugin_multiple_faq.faqplugin': {
            'Meta': {'object_name': 'FAQPlugin', 'db_table': "'cmsplugin_faqplugin'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'faq_list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cmsplugin_multiple_faq.FAQList']"})
        }
    }

    complete_apps = ['cmsplugin_multiple_faq']
