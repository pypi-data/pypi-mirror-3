# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'LeadAction.phone'
        db.add_column('webleads_leadaction', 'phone',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)

        # Adding field 'LeadAction.answered'
        db.add_column('webleads_leadaction', 'answered',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'LeadAction.phone'
        db.delete_column('webleads_leadaction', 'phone')

        # Deleting field 'LeadAction.answered'
        db.delete_column('webleads_leadaction', 'answered')

    models = {
        'webleads.actiontype': {
            'Meta': {'object_name': 'ActionType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'score': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'webleads.leadaction': {
            'Meta': {'ordering': "('-date',)", 'object_name': 'LeadAction'},
            'action_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webleads.ActionType']"}),
            'answered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lead_info': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webleads.LeadInfo']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'product_key': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'webleads.leadinfo': {
            'Meta': {'object_name': 'LeadInfo'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'score': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        }
    }

    complete_apps = ['webleads']
