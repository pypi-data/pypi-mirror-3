# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LeadInfo'
        db.create_table('webleads_leadinfo', (
            ('session_key', self.gf('django.db.models.fields.CharField')(max_length=40, primary_key=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('score', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('webleads', ['LeadInfo'])

        # Adding model 'ActionType'
        db.create_table('webleads_actiontype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('score', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('webleads', ['ActionType'])

        # Adding model 'LeadAction'
        db.create_table('webleads_leadaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lead_info', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['webleads.LeadInfo'])),
            ('product_key', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('action_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['webleads.ActionType'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('webleads', ['LeadAction'])

    def backwards(self, orm):
        # Deleting model 'LeadInfo'
        db.delete_table('webleads_leadinfo')

        # Deleting model 'ActionType'
        db.delete_table('webleads_actiontype')

        # Deleting model 'LeadAction'
        db.delete_table('webleads_leadaction')

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
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lead_info': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webleads.LeadInfo']"}),
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
