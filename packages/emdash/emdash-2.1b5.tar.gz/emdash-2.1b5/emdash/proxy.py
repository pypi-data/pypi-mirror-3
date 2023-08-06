# $Id: proxy.py,v 1.10 2011/05/20 12:29:09 irees Exp $
import copy
import urllib
import urlparse
import itertools
import traceback
import random
import time
import UserDict, collections
collections.Mapping.register(UserDict.DictMixin)

import json

from hashlib import sha1


def dict_encode(obj):
	return dict((encode.func(k),encode.func(v)) for k,v in obj.iteritems())

def list_encode(obj):
	return list(encode.func(i) for i in obj)

def safe_encode(obj):
	'''Always return something, even if it is useless for serialization'''
	try:
		json.dumps(obj)
	except TypeError:
		obj = str(obj)
	return obj


def encode(obj, *a, **kw):
	obj = getattr(obj, 'json_equivalent', lambda: obj)()
	func = lambda x: x
	if hasattr(obj, 'items'):
		func = dict_encode
	elif hasattr(obj, '__iter__'):
		func = list_encode
	else:
		func = safe_encode
	return func(obj)



# >>> class ComplexEncoder(json.JSONEncoder):
# ...     def default(self, obj):
# ...         if isinstance(obj, complex):
# ...             return [obj.real, obj.imag]
# ...         return json.JSONEncoder.default(self, obj)


class NewStyleBaseException(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message

    message = property(_get_message, _set_message)


class JSONRPCException(NewStyleBaseException):
	def __init__(self, rpcError):
		Exception.__init__(self, rpcError.get('message'))
		self.data = rpcError.get('data')
		self.message = rpcError.get('message')
		self.code = rpcError.get('code')


inst = lambda x:x()
class JSONRPCProxy(object):

	@inst
	class IDGen(object):
		def __init__(self):
			self._hasher = sha1()
			self._id = 0
		def __get__(self, *_, **__):
			self._id += 1
			self._hasher.update(str(self._id))
			self._hasher.update(time.ctime())
			self._hasher.update(str(random.random))
			return self._hasher.hexdigest()


	@classmethod
	def from_url(cls, url, ctxid=None, serviceName=None):
		urlsp = urlparse.urlsplit(url)
		url = '%s://%s' % (urlsp.scheme, urlsp.netloc)
		path = urlsp.path
		if urlsp.query: path = '%s?%s' % (path, urlsp.query)
		if urlsp.fragment: path = '%s#%s' % (path, urlsp.fragment)
		return cls(url, path, serviceName, ctxid)


	def transform_url(*a):
		return a


	def __init__(self, host, path='/jsonrpc', serviceName=None, *args, **kwargs):
		self.serviceURL = host
		self._serviceName = serviceName
		self._path = path
		self.init(*args, **kwargs)
		self.serviceURL, self._path = self._transformURL(host, path)


	def _transformURL(self, serviceURL, path):
		if serviceURL[-1] == '/':
			serviceURL = serviceURL[:-1]
		if path[0] != '/':
			path = '/%s'%path
		if path[-1] != '/' and '?' not in path:
			path = '%s/'%path
		return serviceURL, path


	def init(self, *args, **kwargs):
		pass


	def __getattr__(self, name):
		if self._serviceName != None:
			name = "%s.%s" % (self._serviceName, name)
		return self.__class__(self.serviceURL, path=self._path, serviceName=name)


	def _get_postdata(self, args, kwargs):
		if kwargs.has_key('__args'):
			raise ValueError, 'invalid argument name: __args'
		kwargs['__args'] = args or ()
		postdata = {
			"method": self._serviceName,
			'params': kwargs,
			'id': self.IDGen,
			'jsonrpc': '2.0'
		}
	 	return json.dumps(postdata, default=encode)


	def _proc_response(self, data):
		return data


	def __call__(self, *args, **kwargs):
		# print "-> ", self._serviceName
		
		url = '%(host)s%(path)s' % dict(host = self.serviceURL, path = self._path)
		postdata = self._get_postdata(args, kwargs)
		respdata = urllib.urlopen(url, postdata).read()
		resp = json.loads(respdata)

		if resp.get('error') != None:
			raise JSONRPCException(resp['error'])
		else:
			resp = self._proc_response(resp)
			result = resp['result']
			return result


	def _call(self, method, *args, **kwargs):
		p = self.__class__(self.serviceURL, path=self._path, serviceName=method)
		return p(*args, **kwargs)
		

	def batch_call(self, names, *params):
		methods = ( (getattr(self, name),param) for name,param in itertools.izip(names, params) )
		data = (method._get_postdata(params) for method, params in methods)
		postdata = '[%s]' % ','.join(data)
		respdata = urllib.urlopen(self.serviceURL, postdata).read()
		resp = json.dumps(respdata, default=encode)
		return [res.get('result', res.get('error')) for res in resp]


##################################


def zipdicts(*dicts):
	keydict = dicts[0]
	for k in keydict.iterkeys():
		yield (k, tuple(dict_.get(k) for dict_ in dicts))




def newthing(typ):
	def _inner(data):
		a = object.__new__(typ)
		a.update(data)
		return a
	return _inner




class Context(object):
	def __init__(self, ctxid, host):
		self.ctxid = ctxid
		self.host = host
		self.db = None





##################################
# Main exported DB interface classes
##################################


# JSONRPCProxy customized for EMEN2

class EMEN2JSONRPCProxy(JSONRPCProxy):
	def init(self, ctxid=None, t=False, *args, **kwargs):
		self._ctx = Context(ctxid, self.serviceURL)
		self._host = self.serviceURL
		self._ctx.db = self
		self._convert = True
		self._t = t

	# def _transformURL(self, url, path):
	# 	if self._t:
	# 		path = '/?'.join([path, 't=1'])
	# 	return url, path

	typemapping = dict(
		set = set,
		tuple = tuple,
	)
	revmap = dict( (y,x) for x,y in typemapping.iteritems() )


	def _restore_from_typemap(self, typemap, val):
		result = val
		containertype = None
		if isinstance(typemap, list):
			result = {}
			for k, (vv, tv) in zipdicts(val, typemap[1]):
				result[k] = self._restore_from_typemap(tv, vv)
			containertype=self.typemapping.get(typemap[0])
		else:
			containertype=self.typemapping.get(typemap)
		if containertype is not None:
			result = containertype(result)
		return result


	def __getattr__(self, name):
		result = JSONRPCProxy.__getattr__(self, name)
		result._setContext(self._ctx.ctxid)
		return result


	def _setContext(self, ctxid):
		self._ctx.ctxid = ctxid


	def _get_postdata(self, args, kwargs):
		if self._ctx.ctxid:
			kwargs['ctxid'] = self._ctx.ctxid
		return JSONRPCProxy._get_postdata(self, args, kwargs)


	def _proc_response(self, data):
		result = copy.deepcopy(data['result'])
		typemap = copy.deepcopy(data.get('type'))
		if typemap:
			result = self._restore_from_typemap(typemap, result)
		result = dict(
			result = result
		)
		return result


	def login(self, name, password):
		self._ctx.ctxid = self._call('login', name, password)




__version__ = "$Revision: 1.10 $".split(":")[1][:-1].strip()

