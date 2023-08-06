import os
from ConfigParser import SafeConfigParser
import re

_lib_dir = os.path.abspath(os.path.dirname(__file__))
_config = SafeConfigParser()
_read_files = _config.read([
    os.path.join(_lib_dir, 'defaults.cfg'),
    os.path.expanduser('~/.jarmodmoo.cfg'),
    'jarmodmoo.cfg',
    ])


INTERNAL_SERVICE_PREFIX = "mmi."
INTERNAL_SERVICE_REGEX = re.compile(r"^mmi\.(\w+)$")
HEARTBEAT_LIVENESS = _config.getint('heartbeat', 'liveness')
HEARTBEAT_INTERVAL = _config.getint('heartbeat', 'interval')
HEARTBEAT_EXPIRY = HEARTBEAT_INTERVAL * HEARTBEAT_LIVENESS

BROKER_BIND = _config.get('broker', 'bind')

CLIENT_CONNECT = _config.get('client', 'connect')

WORKER_CONNECT = _config.get('worker', 'connect')
WORKER_RECONNECT_DELAY = _config.getint('worker', 'reconnect_delay')
