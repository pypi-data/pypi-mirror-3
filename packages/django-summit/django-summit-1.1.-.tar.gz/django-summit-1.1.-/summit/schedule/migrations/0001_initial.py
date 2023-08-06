# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Summit'
        db.create_table('schedule_summit', (
            ('description', self.gf('django.db.models.fields.TextField')(max_length=2047, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('date_end', self.gf('django.db.models.fields.DateField')(null=True)),
            ('date_start', self.gf('django.db.models.fields.DateField')(null=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default=u'sponsor', max_length=10)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('timezone', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('summit.schedule.fields.NameField')(max_length=50)),
        ))
        db.send_create_signal('schedule', ['Summit'])

        # Adding model 'Track'
        db.create_table('schedule_track', (
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('summit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Summit'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('schedule', ['Track'])

        # Adding model 'Topic'
        db.create_table('schedule_topic', (
            ('summit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Summit'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('schedule', ['Topic'])

        # Adding model 'Slot'
        db.create_table('schedule_slot', (
            ('start_utc', self.gf('django.db.models.fields.DateTimeField')(db_column='start')),
            ('summit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Summit'])),
            ('type', self.gf('django.db.models.fields.CharField')(default=u'open', max_length=7)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('end_utc', self.gf('django.db.models.fields.DateTimeField')(db_column='end')),
        ))
        db.send_create_signal('schedule', ['Slot'])

        # Adding model 'Room'
        db.create_table('schedule_room', (
            ('name', self.gf('summit.schedule.fields.NameField')(max_length=50)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('start_utc', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column='start', blank=True)),
            ('icecast_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('summit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Summit'])),
            ('end_utc', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column='end', blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default=u'open', max_length=7)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('size', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('schedule', ['Room'])

        # Adding M2M table for field tracks on 'Room'
        db.create_table('schedule_room_tracks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('room', models.ForeignKey(orm['schedule.room'], null=False)),
            ('track', models.ForeignKey(orm['schedule.track'], null=False))
        ))
        db.create_unique('schedule_room_tracks', ['room_id', 'track_id'])

        # Adding model 'RoomBusy'
        db.create_table('schedule_roombusy', (
            ('start_utc', self.gf('django.db.models.fields.DateTimeField')(db_column='start')),
            ('end_utc', self.gf('django.db.models.fields.DateTimeField')(db_column='end')),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(related_name='busy_set', to=orm['schedule.Room'])),
        ))
        db.send_create_signal('schedule', ['RoomBusy'])

        # Adding model 'Attendee'
        db.create_table('schedule_attendee', (
            ('start_utc', self.gf('django.db.models.fields.DateTimeField')(db_column='start')),
            ('crew', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='crew', blank=True)),
            ('summit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Summit'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('end_utc', self.gf('django.db.models.fields.DateTimeField')(db_column='end')),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('schedule', ['Attendee'])

        # Adding M2M table for field tracks on 'Attendee'
        db.create_table('schedule_attendee_tracks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('attendee', models.ForeignKey(orm['schedule.attendee'], null=False)),
            ('track', models.ForeignKey(orm['schedule.track'], null=False))
        ))
        db.create_unique('schedule_attendee_tracks', ['attendee_id', 'track_id'])

        # Adding M2M table for field topics on 'Attendee'
        db.create_table('schedule_attendee_topics', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('attendee', models.ForeignKey(orm['schedule.attendee'], null=False)),
            ('topic', models.ForeignKey(orm['schedule.topic'], null=False))
        ))
        db.create_unique('schedule_attendee_topics', ['attendee_id', 'topic_id'])

        # Adding model 'AttendeeBusy'
        db.create_table('schedule_attendeebusy', (
            ('start_utc', self.gf('django.db.models.fields.DateTimeField')(db_column='start')),
            ('attendee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='busy_set', to=orm['schedule.Attendee'])),
            ('end_utc', self.gf('django.db.models.fields.DateTimeField')(db_column='end')),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('schedule', ['AttendeeBusy'])

        # Adding model 'Meeting'
        db.create_table('schedule_meeting', (
            ('status', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('pad_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=2047, blank=True)),
            ('wiki_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('scribe', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='scribe_set', null=True, to=orm['schedule.Attendee'])),
            ('approver', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='approver_set', null=True, to=orm['schedule.Attendee'])),
            ('private', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('assignee', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assignee_set', null=True, to=orm['schedule.Attendee'])),
            ('summit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Summit'])),
            ('videographer2', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='videographer2_set', null=True, to=orm['schedule.Attendee'])),
            ('videographer1', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='videographer1_set', null=True, to=orm['schedule.Attendee'])),
            ('drafter', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='drafter_set', null=True, to=orm['schedule.Attendee'])),
            ('slots', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('spec_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default=u'blueprint', max_length=15)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('summit.schedule.fields.NameField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('schedule', ['Meeting'])

        # Adding M2M table for field tracks on 'Meeting'
        db.create_table('schedule_meeting_tracks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('meeting', models.ForeignKey(orm['schedule.meeting'], null=False)),
            ('track', models.ForeignKey(orm['schedule.track'], null=False))
        ))
        db.create_unique('schedule_meeting_tracks', ['meeting_id', 'track_id'])

        # Adding M2M table for field topics on 'Meeting'
        db.create_table('schedule_meeting_topics', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('meeting', models.ForeignKey(orm['schedule.meeting'], null=False)),
            ('topic', models.ForeignKey(orm['schedule.topic'], null=False))
        ))
        db.create_unique('schedule_meeting_topics', ['meeting_id', 'topic_id'])

        # Adding model 'Participant'
        db.create_table('schedule_participant', (
            ('attendee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Attendee'])),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('meeting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Meeting'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('schedule', ['Participant'])

        # Adding model 'Agenda'
        db.create_table('schedule_agenda', (
            ('slot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Slot'])),
            ('auto', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('meeting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Meeting'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Room'])),
        ))
        db.send_create_signal('schedule', ['Agenda'])

        # Adding unique constraint on 'Agenda', fields ['slot', 'room']
        db.create_unique('schedule_agenda', ['slot_id', 'room_id'])

        # Adding model 'Crew'
        db.create_table('schedule_crew', (
            ('attendee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='crew_schedule', to=orm['schedule.Attendee'])),
            ('date_utc', self.gf('django.db.models.fields.DateField')(db_column='date')),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('schedule', ['Crew'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Summit'
        db.delete_table('schedule_summit')

        # Deleting model 'Track'
        db.delete_table('schedule_track')

        # Deleting model 'Topic'
        db.delete_table('schedule_topic')

        # Deleting model 'Slot'
        db.delete_table('schedule_slot')

        # Deleting model 'Room'
        db.delete_table('schedule_room')

        # Removing M2M table for field tracks on 'Room'
        db.delete_table('schedule_room_tracks')

        # Deleting model 'RoomBusy'
        db.delete_table('schedule_roombusy')

        # Deleting model 'Attendee'
        db.delete_table('schedule_attendee')

        # Removing M2M table for field tracks on 'Attendee'
        db.delete_table('schedule_attendee_tracks')

        # Removing M2M table for field topics on 'Attendee'
        db.delete_table('schedule_attendee_topics')

        # Deleting model 'AttendeeBusy'
        db.delete_table('schedule_attendeebusy')

        # Deleting model 'Meeting'
        db.delete_table('schedule_meeting')

        # Removing M2M table for field tracks on 'Meeting'
        db.delete_table('schedule_meeting_tracks')

        # Removing M2M table for field topics on 'Meeting'
        db.delete_table('schedule_meeting_topics')

        # Deleting model 'Participant'
        db.delete_table('schedule_participant')

        # Deleting model 'Agenda'
        db.delete_table('schedule_agenda')

        # Removing unique constraint on 'Agenda', fields ['slot', 'room']
        db.delete_unique('schedule_agenda', ['slot_id', 'room_id'])

        # Deleting model 'Crew'
        db.delete_table('schedule_crew')
    
    
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
        'schedule.agenda': {
            'Meta': {'unique_together': "(('slot', 'room'),)", 'object_name': 'Agenda'},
            'auto': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Meeting']"}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Room']"}),
            'slot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Slot']"})
        },
        'schedule.attendee': {
            'Meta': {'object_name': 'Attendee'},
            'crew': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'crew'", 'blank': 'True'}),
            'end_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'end'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'start'"}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Topic']", 'symmetrical': 'False', 'blank': 'True'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Track']", 'symmetrical': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'schedule.attendeebusy': {
            'Meta': {'object_name': 'AttendeeBusy'},
            'attendee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'busy_set'", 'to': "orm['schedule.Attendee']"}),
            'end_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'end'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'start'"})
        },
        'schedule.crew': {
            'Meta': {'object_name': 'Crew'},
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
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Attendee']", 'symmetrical': 'False', 'through': "orm['schedule.Participant']", 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
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
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'schedule.room': {
            'Meta': {'object_name': 'Room'},
            'end_utc': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'end'", 'blank': 'True'}),
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
            'Meta': {'object_name': 'RoomBusy'},
            'end_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'end'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'busy_set'", 'to': "orm['schedule.Room']"}),
            'start_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'start'"})
        },
        'schedule.slot': {
            'Meta': {'object_name': 'Slot'},
            'end_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'end'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_utc': ('django.db.models.fields.DateTimeField', [], {'db_column': "'start'"}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "u'open'", 'max_length': '7'})
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
        'schedule.topic': {
            'Meta': {'object_name': 'Topic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'schedule.track': {
            'Meta': {'object_name': 'Track'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'summit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Summit']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['schedule']
