# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Track.allow_adjacent_sessions'
        db.add_column('schedule_track', 'allow_adjacent_sessions', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Track.allow_adjacent_sessions'
        db.delete_column('schedule_track', 'allow_adjacent_sessions')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'schedule.agenda': {
            'Meta': {'ordering': "('slot', 'room')", 'unique_together': "(('slot', 'room'),)", 'object_name': 'Agenda'},
            'auto': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Meeting']"}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Room']"}),
            'slot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Slot']"})
        },
        'schedule.attendee': {
            'Meta': {'ordering': "('summit', 'user')", 'object_name': 'Attendee'},
            'crew': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'crew'"}),
            'end_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'end'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'secret_key_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'start_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'start'"}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Topic']", 'symmetrical': 'False', 'blank': 'True'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Track']", 'symmetrical': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'schedule.attendeebusy': {
            'Meta': {'ordering': "('attendee', 'start_utc', 'end_utc')", 'object_name': 'AttendeeBusy'},
            'attendee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'busy_set'", 'to': "orm['schedule.Attendee']"}),
            'end_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'end'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'start'"})
        },
        'schedule.crew': {
            'Meta': {'ordering': "('date_utc', 'attendee')", 'object_name': 'Crew'},
            'attendee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'crew_schedule'", 'to': "orm['schedule.Attendee']"}),
            'date_utc': ('django.db.models.fields.DateField', [], {'db_column': "'date'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'schedule.meeting': {
            'Meta': {'object_name': 'Meeting'},
            'approver': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'approver_set'", 'null': 'True', 'to': "orm['schedule.Attendee']"}),
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assignee_set'", 'null': 'True', 'to': "orm['schedule.Attendee']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2047', 'blank': 'True'}),
            'drafter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'drafter_set'", 'null': 'True', 'to': "orm['schedule.Attendee']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('summit.schedule.fields.NameField', [], {'max_length': '50', 'blank': 'True'}),
            'pad_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Attendee']", 'symmetrical': 'False', 'through': "'Participant'", 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requires_dial_in': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'scribe': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'scribe_set'", 'null': 'True', 'to': "orm['schedule.Attendee']"}),
            'slots': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'spec_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Topic']", 'symmetrical': 'False', 'blank': 'True'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Track']", 'symmetrical': 'False', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "u'blueprint'", 'max_length': '15'}),
            'videographer1': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'videographer1_set'", 'null': 'True', 'to': "orm['schedule.Attendee']"}),
            'videographer2': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'videographer2_set'", 'null': 'True', 'to': "orm['schedule.Attendee']"}),
            'wiki_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'schedule.participant': {
            'Meta': {'object_name': 'Participant'},
            'attendee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Attendee']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Meeting']"}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'schedule.room': {
            'Meta': {'ordering': "('summit', 'name')", 'object_name': 'Room'},
            'end_utc': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'end'", 'blank': 'True'}),
            'has_dial_in': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'icecast_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('summit.schedule.fields.NameField', [], {'max_length': '50'}),
            'size': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start_utc': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'start'", 'blank': 'True'}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Track']", 'symmetrical': 'False', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "u'open'", 'max_length': '7'})
        },
        'schedule.roombusy': {
            'Meta': {'ordering': "('room', 'start_utc', 'end_utc')", 'object_name': 'RoomBusy'},
            'end_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'end'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'busy_set'", 'to': "orm['schedule.Room']"}),
            'start_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'start'"})
        },
        'schedule.slot': {
            'Meta': {'ordering': "('summit', 'start_utc', 'end_utc')", 'object_name': 'Slot'},
            'end_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'end'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'start'"}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "u'open'", 'max_length': '7'})
        },
        'schedule.summit': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Summit'},
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
        'schedule.summitsprint': {
            'Meta': {'ordering': "('summit', 'import_url')", 'object_name': 'SummitSprint'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sprint_set'", 'to': "orm['schedule.Summit']"})
        },
        'schedule.topic': {
            'Meta': {'ordering': "('summit', 'title')", 'object_name': 'Topic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'schedule.track': {
            'Meta': {'ordering': "('summit', 'title', 'slug')", 'object_name': 'Track'},
            'allow_adjacent_sessions': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'color': ('django.db.models.fields.CharField', [], {'default': "'FFFFFF'", 'max_length': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['schedule']
