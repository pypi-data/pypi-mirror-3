#encoding:utf-8
from django.contrib import admin
from helmholtz.recording.models import RecordingBlock, ProtocolRecording

class RecordingBlockAdmin(admin.ModelAdmin):
    list_display = ['label', 'experiment']

recording_admin = admin.site

recording_admin.register(RecordingBlock, RecordingBlockAdmin)
recording_admin.register(ProtocolRecording)

