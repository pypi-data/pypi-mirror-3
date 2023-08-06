# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Sponsorship'
        db.create_table('sponsor_sponsorship', (
            ('about', self.gf('django.db.models.fields.TextField')(max_length=1000)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('needs_travel', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('further_info', self.gf('django.db.models.fields.TextField')(max_length=1000, blank=True)),
            ('diet', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('needs_accomodation', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('summit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Summit'])),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('would_crew', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('video_agreement', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('sponsor', ['Sponsorship'])

        # Adding model 'SponsorshipScore'
        db.create_table('sponsor_sponsorshipscore', (
            ('comment', self.gf('django.db.models.fields.TextField')(max_length=500, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('score', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sponsorship', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sponsor.Sponsorship'])),
        ))
        db.send_create_signal('sponsor', ['SponsorshipScore'])

        # Adding model 'NonLaunchpadSponsorship'
        db.create_table('sponsor_nonlaunchpadsponsorship', (
            ('about', self.gf('django.db.models.fields.TextField')(max_length=1000)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('needs_travel', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('further_info', self.gf('django.db.models.fields.TextField')(max_length=1000, blank=True)),
            ('needs_accomodation', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('diet', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('requested_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('summit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Summit'])),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('would_crew', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('sponsor', ['NonLaunchpadSponsorship'])

        # Adding model 'NonLaunchpadSponsorshipScore'
        db.create_table('sponsor_nonlaunchpadsponsorshipscore', (
            ('comment', self.gf('django.db.models.fields.TextField')(max_length=500, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('score', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sponsorship', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sponsor.NonLaunchpadSponsorship'])),
        ))
        db.send_create_signal('sponsor', ['NonLaunchpadSponsorshipScore'])

        # Adding model 'SponsorshipSuggestion'
        db.create_table('sponsor_sponsorshipsuggestion', (
            ('launchpad_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('about', self.gf('django.db.models.fields.TextField')(max_length=1000)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('needs_travel', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('further_info', self.gf('django.db.models.fields.TextField')(max_length=1000, blank=True)),
            ('diet', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('needs_accomodation', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('summit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Summit'])),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('would_crew', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('suggested_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('sponsor', ['SponsorshipSuggestion'])

        # Adding model 'SponsorshipSuggestionScore'
        db.create_table('sponsor_sponsorshipsuggestionscore', (
            ('comment', self.gf('django.db.models.fields.TextField')(max_length=500, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('score', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sponsorship', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sponsor.SponsorshipSuggestion'])),
        ))
        db.send_create_signal('sponsor', ['SponsorshipSuggestionScore'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Sponsorship'
        db.delete_table('sponsor_sponsorship')

        # Deleting model 'SponsorshipScore'
        db.delete_table('sponsor_sponsorshipscore')

        # Deleting model 'NonLaunchpadSponsorship'
        db.delete_table('sponsor_nonlaunchpadsponsorship')

        # Deleting model 'NonLaunchpadSponsorshipScore'
        db.delete_table('sponsor_nonlaunchpadsponsorshipscore')

        # Deleting model 'SponsorshipSuggestion'
        db.delete_table('sponsor_sponsorshipsuggestion')

        # Deleting model 'SponsorshipSuggestionScore'
        db.delete_table('sponsor_sponsorshipsuggestionscore')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'schedule.summit': {
            'Meta': {'object_name': 'Summit'},
            'date_end': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_start': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2047', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('summit.schedule.fields.NameField', [], {'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "u'sponsor'", 'max_length': '10'}),
            'timezone': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sponsor.nonlaunchpadsponsorship': {
            'Meta': {'object_name': 'NonLaunchpadSponsorship'},
            'about': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'diet': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'further_info': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'needs_accomodation': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'needs_travel': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'requested_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'would_crew': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'sponsor.nonlaunchpadsponsorshipscore': {
            'Meta': {'object_name': 'NonLaunchpadSponsorshipScore'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {}),
            'sponsorship': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sponsor.NonLaunchpadSponsorship']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'sponsor.sponsorship': {
            'Meta': {'object_name': 'Sponsorship'},
            'about': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'diet': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'further_info': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'needs_accomodation': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'needs_travel': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'video_agreement': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'would_crew': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'sponsor.sponsorshipscore': {
            'Meta': {'object_name': 'SponsorshipScore'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {}),
            'sponsorship': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sponsor.Sponsorship']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'sponsor.sponsorshipsuggestion': {
            'Meta': {'object_name': 'SponsorshipSuggestion'},
            'about': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'diet': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'further_info': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'launchpad_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'needs_accomodation': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'needs_travel': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'suggested_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'would_crew': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'sponsor.sponsorshipsuggestionscore': {
            'Meta': {'object_name': 'SponsorshipSuggestionScore'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {}),
            'sponsorship': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sponsor.SponsorshipSuggestion']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }
    
    complete_apps = ['sponsor']
