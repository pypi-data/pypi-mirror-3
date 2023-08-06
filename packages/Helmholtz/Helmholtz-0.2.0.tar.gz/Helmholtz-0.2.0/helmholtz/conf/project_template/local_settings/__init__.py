import socket
from helmholtz.core.loggers import create_console

logging = create_console('local_settings')
hostname = socket.gethostname()

VERSIONS = {
    #Example :        
    #'hostname':'package'
}

if hostname in VERSIONS:
    VERSION = VERSIONS[hostname]
    exec("from %s import *" % VERSION)
else :
    logging.warning("cannot import local settings, configure VERSIONS dictionary in local_settings.__init__.py file.")


