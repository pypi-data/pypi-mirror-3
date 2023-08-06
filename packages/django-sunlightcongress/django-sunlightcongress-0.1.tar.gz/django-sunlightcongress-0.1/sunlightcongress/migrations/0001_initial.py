# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Legislator'
        db.create_table('sunlightcongress_legislator', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('middlename', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('name_suffix', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('party', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('in_office', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('fax', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=1024, null=True, blank=True)),
            ('webform', self.gf('django.db.models.fields.URLField')(max_length=1024, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=254, null=True, blank=True)),
            ('congress_office', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('bioguide_id', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True)),
            ('votesmart_id', self.gf('django.db.models.fields.IntegerField')(unique=True, null=True, blank=True)),
            ('fec_id', self.gf('django.db.models.fields.CharField')(max_length=16, unique=True, null=True, blank=True)),
            ('govtrack_id', self.gf('django.db.models.fields.IntegerField')(unique=True, null=True, blank=True)),
            ('crp_id', self.gf('django.db.models.fields.CharField')(max_length=16, unique=True, null=True, blank=True)),
            ('congresspedia_url', self.gf('django.db.models.fields.URLField')(max_length=1024, null=True, blank=True)),
            ('twitter_id', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('youtube_url', self.gf('django.db.models.fields.URLField')(max_length=1024, null=True, blank=True)),
            ('facebook_id', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('senate_class', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('official_rss', self.gf('django.db.models.fields.URLField')(max_length=1024, null=True, blank=True)),
            ('birthdate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('sunlightcongress', ['Legislator'])

        # Adding model 'Committee'
        db.create_table('sunlightcongress_committee', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=6, primary_key=True)),
            ('chamber', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sunlightcongress.Committee'], null=True)),
        ))
        db.send_create_signal('sunlightcongress', ['Committee'])

        # Adding M2M table for field members on 'Committee'
        db.create_table('sunlightcongress_committee_members', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('committee', models.ForeignKey(orm['sunlightcongress.committee'], null=False)),
            ('legislator', models.ForeignKey(orm['sunlightcongress.legislator'], null=False))
        ))
        db.create_unique('sunlightcongress_committee_members', ['committee_id', 'legislator_id'])


    def backwards(self, orm):
        # Deleting model 'Legislator'
        db.delete_table('sunlightcongress_legislator')

        # Deleting model 'Committee'
        db.delete_table('sunlightcongress_committee')

        # Removing M2M table for field members on 'Committee'
        db.delete_table('sunlightcongress_committee_members')


    models = {
        'sunlightcongress.committee': {
            'Meta': {'ordering': "['name']", 'object_name': 'Committee'},
            'chamber': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '6', 'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sunlightcongress.Legislator']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sunlightcongress.Committee']", 'null': 'True'})
        },
        'sunlightcongress.legislator': {
            'Meta': {'ordering': "['lastname', 'firstname']", 'object_name': 'Legislator'},
            'bioguide_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'birthdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'congress_office': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'congresspedia_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'crp_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'govtrack_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'in_office': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'middlename': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'name_suffix': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'official_rss': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'senate_class': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'votesmart_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'webform': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'youtube_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['sunlightcongress']