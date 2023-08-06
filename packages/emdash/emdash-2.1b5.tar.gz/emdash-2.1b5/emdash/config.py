import os
import time
import optparse
import getpass
import datetime
import dateutil
import dateutil.tz
# Distutils
# import distutils.version


##################################
# Global Config
##################################

config = {}
config['film_types'] = ['so-163', 'so163', 'kodak', 'film']

config['starclosed'] = u"\u2605"
config['staropen'] = u"\u2606"
config['sleeptime'] = 1
config['restart'] = False

config['DEBUG'] = False
config['DEBUG_RECIDS'] = {}

config['USER_AGENT'] = "emen2client" #/%s"%__version__
config['host'] = os.getenv("EMEN2URI", "http://ncmidb.bcm.edu")


def get(key, default=None):
	return config.get(key, default)
	
def set(key, value):
	config[key] = value
	
def update(update):
	return config.update(update)	


##### Logging #####
listeners = []
def addlistener(func):
	listeners.append(func)

def log(msg=None, progress='', f=''):
	t = time.strftime('%Y/%m/%d %H:%M:%S')
	if msg:
		print t, msg, progress, f
	for listener in listeners:
		listener(msg=msg, progress=progress, f=f)


##################################
# Exported utility methods
##################################

tzlocal = dateutil.tz.gettz()
def gettime():
	return datetime.datetime.now(tzlocal).isoformat()


def copydb(db):
	import emdash.proxy
	return emdash.proxy.EMEN2JSONRPCProxy(host=db._host, ctxid=db._ctx.ctxid)


##################################
# Options
##################################

class DBRPCOptions(optparse.OptionParser):
	"""Default options to be used by EMEN2 clients"""

	def __init__(self, *args, **kwargs):
		optparse.OptionParser.__init__(self, *args, **kwargs)
		self.add_option("--name","-U", type="string", help="Account name or email")
		self.add_option("--password","-P", type="string", help="Password (Note: specifying passwords in shell commands is not secure)")
		self.add_option("--host","-H", type="string", help="Host endpoint URI; default is %s, or environment variable EMEN2URI"%get('host'), default=get('host'))


	def parse_args(self, lc=True, *args, **kwargs):
		r1, r2 = optparse.OptionParser.parse_args(self,  *args, **kwargs)
		config['host'] = self.values.host
		config['name'] = self.values.name
		return r1, r2
		
		
	def opendb(self, name=None, password=None, ctxid=None, request=False):
		import emdash.proxy		
		db = emdash.proxy.EMEN2JSONRPCProxy(host=self.values.host, ctxid=ctxid)
		
		name = name or self.values.name
		if request and not name:
			name = raw_input("Email: ")
		
		if name:
			password = password or self.values.password
			if password is None:
				password = getpass.getpass("Password: ")
			db.login(name=name, password=password)

		return db


	# def checkversion(self):
	# 	v = self.db.checkversion("emen2client")
	# 
	# 	if distutils.version.StrictVersion(emdash.__version__) < distutils.version.StrictVersion(v):
	# 		print """
	# Note: emen2client version %s is available; installed version is %s.
	# """%(v, __version__)
	# 
	# 	else:
	# 		print "emen2client version %s is up to date"%(__version__)
