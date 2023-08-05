
from distutils import version
import connector

FEATURES = (
	('operator_$or', '1.5.3'),
)
MONGODB_SERVER_INFO = None
_curr_version = None

def get_mongodb_server_info():
	global MONGODB_SERVER_INFO, _curr_version
	if not MONGODB_SERVER_INFO:
		MONGODB_SERVER_INFO = connector.db_instance._cn.server_info()
	
	_curr_version = version.StrictVersion(MONGODB_SERVER_INFO['version'])
	return MONGODB_SERVER_INFO

def is_support(feature):
	global FEATURES, _curr_version
	get_mongodb_server_info()
	for f in FEATURES:
		if f[0] == feature:
			needs_version = version.StrictVersion(f[1])
			if _curr_version >= needs_version:
				return True
			break
	return False



