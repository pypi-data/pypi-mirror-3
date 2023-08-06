import collections
import copy
import glob
import math
import os
import struct
import subprocess
import tempfile
import time

import datetime
import dateutil
import dateutil.tz

# XML Etree -- Generally available on Python 2.5+
try:
	import xml.etree.ElementTree as ET
except ImportError:
	ET = None

import emdash.config
import emdash.transport

##### Base FileHandler #####

class FileHandler(object):
	exts = ['.dm3', '.tif', '.tiff', '.hdf5', '.h5', '.st', '.mrc']
	rectype = None

	def __init__(self, db=None, name=None, filename=None, filedata=None, applyparams=None, **kwargs):
		"""Provide special support for different filetypes
		@keyparam db DBProxy
		@keyparam name Record ID for download or upload
		@keyparam filename Filename for upload
		@keyparam applyparams Parameters to overlay on new records (see: CCDHandler)
		"""
		# db handle
		self.db = db
		# target record name for upload or download
		self.name = name

		# file to upload
		self.filename = filename
		self.filedata = filedata

		# values to apply to new records
		self.applyparams = applyparams or {}

		# reporting attributes
		self.progress = 0.0
		self.uploaded = {}

	##### Upload #####

	def poll(self, path, seen=None):
		"""Get files, sort by ctime"""
		
		path = unicode(path)
		if seen is None:
			seen = set()
		if not path:
			return

		files = []
		for f in os.walk(path):
			for fi in f[2]:
				fi = os.path.join(f[0], fi)
				if self.checkfile(fi) and fi not in seen:
					files.append(fi)
					seen |= set(files)

		def ctime(filename):
			return os.stat(filename).st_ctime

		return sorted(files, key=ctime)

	def checkfile(self, filename):
		# Decide to ignore the file, or add to queue
		ext = os.path.splitext(filename)[-1].lower()
		if ext in self.exts:
			return filename
		
	def checkrecname(self):
		"""String to display in the upload queue."""
		return os.path.basename(self.filename)
		
	def log(self, msg=None, progress=None, f=None):
		emdash.config.log(msg=msg, progress=progress, f=self.filename)


	######################
	# Upload
	######################

	def upload(self):
		"""Start the upload process for this handler"""
		
		self.log("\n--- %s"%self.filename)
		self.log("Preparing for upload")
		self.check_db()
		files = self.get_upload_items()
		self.log("Starting upload")
		
		# Upload files
		filecount = len(files)
		for count, f in enumerate(files):
			f.setdb(self.db)
			self.uploaded[f.filename] = f.action()

		# todo: make this sane.
		if self.uploaded:
			return self.uploaded.values()[-1]
		
		
		
	def get_upload_items(self):
		"""Returns records and files to upload"""
		newrecord = {}
		newrecord['rectype'] = self.rectype
		newrecord.update(self.applyparams)
		
		# Try to get the file creation time
		ct = os.path.getctime(self.filename)
		t = datetime.datetime.fromtimestamp(ct).replace(tzinfo=emdash.config.tzlocal)
		# print "setting date_occurred to...", t.isoformat()
		newrecord['date_occurred'] = t.isoformat()
		
		f = emdash.transport.UploadTransport(name=self.name, filename=self.filename, newrecord=newrecord)
		return [f]
		

	def check_db(self):
		pass


class AutoHandler(FileHandler):
	pass
	

#################################
# Filetype-specific handlers
##################################


class VolumeHandler(FileHandler):
	rectype = 'volume'
	

class GridImagingFileHandler(FileHandler):
	def check_db(self):
		gi = self.db.getrecord(self.name, filt=False)
		if gi.get("rectype") != "grid_imaging":
			# raise Exception, 
			self.log("WARNING! This action may only be used with grid_imaging sessions!")

		microscopy = self.db.getparents(self.name, 1, ["microscopy"])
		if not microscopy:
			self.log("WARNING! No microscopy record present for grid_imaging session!")


class MicrographHandler(GridImagingFileHandler):
	rectype = 'micrograph'
	

class DDDHandler(GridImagingFileHandler):
	rectype = 'ddd'

	
class JADASHandler(GridImagingFileHandler):
	rectype = 'ccd_jadas'


class CCDHandler(GridImagingFileHandler):
	rectype = 'ccd'


class ScanHandler(GridImagingFileHandler):
	rectype = 'scan'


class StackHandler(GridImagingFileHandler):
	rectype = 'stack'


##################################
# Util
##################################

map_rectype_handler = {
	"ccd": CCDHandler,
	"stack": StackHandler,
	"scan": ScanHandler,
	"volume": VolumeHandler,
	"micrograph": MicrographHandler,
	"ddd": DDDHandler,
	"ccd_jadas": JADASHandler,
	"none": FileHandler
}

map_filename_rectype = {
	'.st': 'stack',
	'.dm3': 'ccd',
	'.tif': 'ddd',
	'.mrc': 'scan'
}



def get_handler(rectype=None, filename=None):
	if rectype:
		return map_rectype_handler.get(rectype, FileHandler)
	elif filename:
		ext = os.path.splitext(filename or '')[-1]
		rectype = map_filename_rectype.get(ext)
		return map_rectype_handler.get(rectype, FileHandler)
	else:
		return FileHandler




__version__ = "$Revision: 1.16 $".split(":")[1][:-1].strip()
