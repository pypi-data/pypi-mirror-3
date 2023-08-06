# We are going to use a great deal of the Standard Library
import StringIO
import gzip
import httplib
import os
import socket
import subprocess
import time
import urllib
import urllib2
import urlparse
import zlib
import json

import emdash.config


##################################
# Exceptions
##################################

class OverwriteError(Exception):
	"""File exists, and flags are set to prevent overwriting"""


##################################
# File Transport
##################################

class Transport(object):
	def __init__(self, db=None, bdo=None, param="file_binary_image", name=None, newrecord=None, filename=None, filedata=None, pos=None):
		"""Transport a file to/from the database.

		@keyparam db DBProxy
		@keyparam bdo BDO object
		@keyparam filename Filename to upload
		@keyparam filedata Upload a buffer instead of a file. In this case, filename will be used for the name of the file.
		"""
		
		self.db = db
		self.bdo = bdo
		self.filename = filename
		self.filedata = filedata

		self.newrecord = newrecord
		self.param = param
		self.name = name

	def _retry(self, method, *args, **kwargs):
		"""Automatic retry wrapper
		@param method self._upload or self._download
		"""

		count = 0
		ret = None
		while True:
			count += 1
			try:
				ret = method(*args, **kwargs)
				break

			except KeyboardInterrupt, e:
				print "Keyboard Interrupt"
				raise

			# socket.error is recoverable, others are not recoverable!
			except socket.error, e:
				self.log("Network error, trying again in 10 seconds (%s attempts): %s"%(count, e))
				time.sleep(10)

			except Exception, e:
				self.log("Unrecoverable error, aborting: %s"%(e))
				raise

		return ret

	def action(self, *args, **kwargs):
		"""Transfer the file."""
		pass

	def log(self, msg=None, progress=None, f=None):
		"""Log"""
		f = (self.bdo or {}).get('name') or self.filename
		emdash.config.log(msg=msg, progress=progress, f=f)

	def setdb(self, db):
		self.db = db

	def sidecar_read(self, filename=None):
		"""Read the JSON sidecar."""
		filename = filename or self.filename
		try:
			return json.load(file(filename+".json","r")) or {}
		except:
			pass

	def sidecar_write(self, filename=None):
		"""Write the JSON sidecar."""
		filename = filename or self.filename
		try:
			json.dump(self.bdo, file(filename+".json", "w"), indent=True)
			self.log("Wrote sidecar: %s.json"%filename)
		except:
			pass





class UploadTransport(Transport):
	"""Upload a file to the DB."""

	def action(self):
		s = self.sidecar_read()
		if s != None:
			self.log("File already exists in database. Check record %s."%s.get("record"))
			self.bdo = s
			self.name = s.get('record', 0) # tody: this is a temporary fix... 
			return

		ret = self._retry(self._upload)
		self.sidecar_write()		
		self.log("Done")
		return ret



	def _upload(self, mimetype=None):
		"""Implements Transfer-Encoding:Chunked over a PUT request, with optional gzip pipe streaming. See upload() for arguments."""

		# Upload a string buffer as a file
		if self.filedata:
			filesize = len(self.filedata)
			fio = StringIO.StringIO(self.filedata)
			filename = self.filename

		# Or upload a file from disk
		else:
			# Get file size for progress bar
			filesize = float(os.stat(self.filename).st_size)
			# Are we compressing this file?
			# fio = GzipPipe(filename=self.filename)
			fio = open(self.filename, "rb")
			filename = os.path.basename(fio.name)

		if filesize == 0:
			self.log("Warning: Uploading empty file!")
			filesize = 1 # avoid div by zero

		qs = {}
		rectype = self.newrecord.pop('rectype')
		qs.update(self.newrecord)
		qs['ctxid'] = self.db._ctx.ctxid

		# Upload the record
		qs = urllib.urlencode(qs)
		host = self.db._host.split("://")[-1]
		path = '/record/%s/new/%s/?%s'%(self.name, rectype, qs)

		# Set headers
		headers = {}
		headers['X-File-Name'] = filename
		headers['X-File-Param'] = self.param
		headers['User-Agent'] = emdash.config.get('USER_AGENT')
		headers['Transfer-Encoding'] = 'chunked'
		if mimetype:
			headers["Content-Type"] = mimetype

		# Open connection
		http = httplib.HTTPConnection(host)
		http.request("PUT", path, headers=headers)

		# Upload in chunks
		t = time.time()
		chunksize = 1024*1024
		
		while True:
			try:
				chunk = fio.read(chunksize)
				cs = len(chunk)
				http.send("%X\r\n"%(cs))
				http.send(chunk)
				http.send("\r\n")
				self.log(progress=(fio.tell()/filesize))
			except socket.error:
				if fio:
					fio.close()
				raise
			if not chunk:
				if fio:
					fio.close()
				break

		# Responses..
		resp = http.getresponse()
		status, reason, response = resp.status, resp.reason, resp.read()
		http.close()

		if status not in range(200, 400):
			raise httplib.HTTPException, "Error: %s"%(reason)

		kbsec = (filesize / (time.time() - t))/1024

		# print 'response:', response
		# response = json.loads(response)
		# self.bdo = response
		name = int(response)
		self.log("Done. Uploaded %s to record %s @ %0.2f kb/sec"%(self.filename, name, kbsec))
		return name



# class DownloadTransport(Transport):
# 
# 	def action(self, overwrite=False, rename=False, sidecar=False, *args, **kwargs):
# 		"""Download BDO to local disk
# 
# 		@keyparam overwrite Overwrite an existing file
# 		@keyparam rename If file exists, rename file to avoid overwriting
# 
# 		"""
# 
# 		try:
# 			# Check that we can download the file, and then get it
# 			self._download_checkfile(overwrite=overwrite, rename=rename)
# 			self.log("Downloading %s -> %s..."%(self.bdo.get("filename"), self.filename))
# 
# 			ret = self._retry(self._download)
# 
# 			if sidecar:
# 				self.sidecar_write()
# 
# 			self.log("Done")
# 
# 		except OverwriteError, e:
# 			# Or report that we can't download it
# 			self.log("Skipping file: %s"%e)
# 			return self.filename
# 
# 		return self.filename
# 
# 
# 
# 
# 	def _download_checkfile(self, overwrite=False, rename=False):
# 		"""Check if we can write the file, and if to use compression or not. See download() for params"""
# 
# 		filename = os.path.basename(self.bdo.get("filename")) or self.bdo.get("name")
# 		fsplit = os.path.splitext(filename)
# 
# 		# this may raise OverwriteError Exception, which should be caught by caller
# 		if os.path.exists(filename) and not overwrite:
# 			if rename:
# 				filename = "duplicate.%s:%s"%(self.bdo.get("name"), filename)
# 			else:
# 				raise OverwriteError, "File exists: %s"%filename
# 
# 		self.filename = filename
# 
# 
# 
# 	def _download(self):
# 		"""Actual download."""
# 
# 		# Setup connection
# 
# 		ctxid = urllib.urlencode({"ctxid":self.db._ctx.ctxid})
# 
# 		# ian: changed .netloc to [1] because it caused failure on python 2.4
# 		up = urlparse.urlparse(self.db._host) # .netloc
# 		host = up[1]
# 		path = "%s/download/%s?%s"%(up[2], self.bdo.get("name"), ctxid)
# 
# 		# Connect
# 		http = httplib.HTTPConnection(host)
# 		http.request("GET", path)
# 		resp = http.getresponse()
# 		#print(resp.getheader('content-length'))
# 		clength = float(resp.getheader('content-length'))
# 
# 		# Download and pipe through gzip
# 		stdout = None
# 		# if self.compress:
# 		# 	stdout = open(self.filename, "wb")
# 		# 	gz = subprocess.Popen(["gzip","-d"], stdout=stdout, stdin=subprocess.PIPE)
# 		# 	fio = gz.stdin
# 		fio = open(self.filename,"wb")
# 
# 		chunksize = 1024*1024
# 		outlen = 0
# 		while outlen < clength:
# 			chunk = resp.read(chunksize)
# 			outlen += len(chunk)
# 			fio.write(chunk)
# 			self.log(progress=(outlen/clength))
# 
# 		self.log("Download complete", progress=1.0)
# 
# 		fio.close()
# 		if stdout: stdout.close()
# 		http.close()
# 
# 		return self.filename



##################################
# Compression schemes
##################################

# Compression is handled on the fly now during upload / download with a gzip pipe

# Based on http://code.activestate.com/recipes/551784/
# class GzipPipe(StringIO.StringIO):
# 	"""This class implements a compression pipe suitable for asynchronous
# 	process."""
# 
# 	# Size of the internal buffer
# 	CHUNCK_SIZE = 1024*1024
# 	COMPRESSLEVEL = 3
# 
# 	def __init__(self, filename=None) :
# 		"""Streaming compression using gzip.GzipFile
# 
# 		@param filename source file
# 
# 		"""
# 
# 		self.filename = filename
# 		self.source = open(self.filename, "rb")
# 		self.source_eof = False
# 		self.buffer = ""
# 		self.name = self.filename + ".gz"
# 
# 		self.pos = 0
# 
# 		StringIO.StringIO.__init__(self)
# 		#super(GzipPipe, self).__init__(self)
# 		self.zipfile = gzip.GzipFile(filename=str(os.path.basename(filename)), mode='wb', compresslevel=self.COMPRESSLEVEL, fileobj=self)
# 
# 
# 	def write(self, data):
# 		"""Writes data to internal buffer. Do not call from outside."""
# 		self.buffer += data
# 
# 
# 	def read(self, size=-1) :
# 		"""Calling read() on a zip pipe will suck data from the source stream.
# 		@param	size Maximum size to read - Read whole compressed file if not specified.
# 		@return Compressed data
# 		"""
# 
# 		# Feed the zipped buffer by writing source data to the zip stream
# 		while ((len(self.buffer) < size) or (size == -1)) and not self.source_eof:
# 
# 			# Get a chunk of source data
# 			chunk = self.source.read(GzipPipe.CHUNCK_SIZE)
# 			self.pos += len(chunk)
# 
# 			# Feed the source zip file (that fills the compressed buffer)
# 			self.zipfile.write(chunk)
# 
# 			# End of source file ?
# 			if (len(chunk) < GzipPipe.CHUNCK_SIZE) :
# 				self.source_eof = True
# 				self.zipfile.flush()
# 				self.zipfile.close()
# 				self.source.close()
# 				break
# 
# 
# 		# We have enough data in the buffer (or source file is EOF): Give it to the output
# 		if size == 0:
# 			result = ""
# 		if size >= 1:
# 			result = self.buffer[0:size]
# 			self.buffer = self.buffer[size:]
# 		else: # size < 0 : All requested
# 			result = self.buffer
# 			self.buffer = ""
# 
# 		return result
# 
