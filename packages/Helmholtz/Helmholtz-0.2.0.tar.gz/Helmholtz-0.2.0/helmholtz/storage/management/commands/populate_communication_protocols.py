#encoding:utf-8
from helmholtz.core.populate import PopulateCommand
from helmholtz.storage.models import CommunicationProtocol

protocols = [
    {'name':'HyperText Transfert Protocol', 'initials':'HTTP'},
    {'name':'Secured HyperText Transfert Protocol', 'initials':'HTTPS'},
    {'name':'File Transfert Protocol', 'initials':'FTP'},
    {'name':'Secured File Transfert Protocol', 'initials':'SFTP'},
    {'name':'Secured SHell', 'initials':'SSH'},
    {'name':'Network File System', 'initials':'NFS'},
    {'name':'Server Message Block', 'initials':'SMB'},
    {'name':'Common Internet File System', 'initials':'CIFS'}
]

class Command(PopulateCommand):
    help = "populate communication protocols"
    priority = 0
    data = [
        {'class':CommunicationProtocol, 'objects':protocols}    
    ]
