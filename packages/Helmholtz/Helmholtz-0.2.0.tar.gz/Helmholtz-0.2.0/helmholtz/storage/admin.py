#encoding:utf-8
from django.contrib import admin
from helmholtz.storage.models import MimeType, CommunicationProtocol, FileServer, FileLocation, File

storage_admin = admin.site

storage_admin.register(MimeType)
storage_admin.register(CommunicationProtocol)
storage_admin.register(File)
storage_admin.register(FileServer)
storage_admin.register(FileLocation)
