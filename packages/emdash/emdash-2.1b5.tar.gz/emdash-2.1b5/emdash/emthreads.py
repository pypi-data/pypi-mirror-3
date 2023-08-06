# $Id: emthreads.py,v 1.15 2012/03/08 11:29:08 irees Exp $
import Queue
import collections
import datetime
import json
import operator
import os
import time

from PyQt4 import QtCore

import emdash.config
import emdash.handlers
import emdash.transport


class DBThread(QtCore.QThread):
	signal_file_status = QtCore.pyqtSignal(unicode, object)
	signal_exception = QtCore.pyqtSignal(unicode)
	def __init__(self, method, args):
		pass
		
		

class ClockThread(QtCore.QThread):
	"""Emit a signal every second with timedelta from start time"""

	signal_tick = QtCore.pyqtSignal(str)

	def __init__(self, starttime=None, parent=None):
		QtCore.QThread.__init__(self, parent=parent)
		self.starttime = starttime
		
	def reset(self):
		self.starttime = time.time()
		
	def run(self):
		self.reset()
		while True:
			if self.starttime == None:
				t = ""
			else:
				t = int(time.time() - self.starttime)
				t = str(datetime.timedelta(seconds=t))

			self.signal_tick.emit(t)		
			time.sleep(1)


	@QtCore.pyqtSlot()	
	def longsleep(self):
		self.sleep(5)



class FSPollThread(QtCore.QThread):
	"""Watch a directory"""

	signal_newfile = QtCore.pyqtSignal(unicode, object)

	def __init__(self, path=None, parent=None): #queue=None, 
		"""Watches a directory for new files"""
		QtCore.QThread.__init__(self, parent=parent)

		self.path = path
		self.seen = set()
		
		# Eventually this will be a selectable handler for polling changes:
		# Different handlers will be able to define their own ways of finding
		# and handling new files.
		self.rectype = None
		self.sethandler(self.rectype)
		

	@QtCore.pyqtSlot(str)
	def sethandler(self, rectype):
		self.handler = emdash.handlers.get_handler(rectype=rectype)()
			

	@QtCore.pyqtSlot(str)
	def setpath(self, path):
		self.seen = set()
		self.path = unicode(path)



	def run(self):
		while True:
			for f in self.handler.poll(path=self.path, seen=self.seen):
				self.newfile(f)		
			time.sleep(5)


	@QtCore.pyqtSlot(unicode)
	def newfile(self, filename):
		# Signal that we have a new file, with some basic info
		filename = unicode(filename)
		h = emdash.handlers.get_handler(filename=filename)()
		data = {
			'_filename': filename,
			'_rectype': h.rectype
		}
		self.signal_newfile.emit(filename, data)


	@QtCore.pyqtSlot(QtCore.QStringList)
	def newfiles(self, filenames):
		for filename in filenames:
			self.newfile(filename)




class UploadThread(QtCore.QThread):
	"""Upload a file"""

	signal_file_failure = QtCore.pyqtSignal(unicode, unicode)
	signal_file_status = QtCore.pyqtSignal(unicode, object)
	signal_file_success = QtCore.pyqtSignal(unicode, object)	

	def __init__(self, parent=None, queue=None, db=None):
		self.db = db
		self.queue = queue
		emdash.config.addlistener(self.log)
		QtCore.QThread.__init__(self, parent=parent)

	def log(self, msg=None, progress=None, f=None):
		self.signal_file_status.emit(f or '', {"_status":msg or progress, "_progress": progress})

	@QtCore.pyqtSlot(unicode)	
	def login_cb(self, ctxid):
		self.db._setContext(unicode(ctxid))
		
	def enqueue(self, filename, item):
		item["_status"] = "Queued"
		self.queue.put(item)
		self.signal_file_status.emit(filename, item)

	def run(self):		
		while True:
			self.action()

	def action(self):
		item = self.queue.get()	
		filename = item.get('_filename')
		name = item.get('_parent')
		rectype = item.get('_rectype')

		if name < 0:
			raise Exception, "UploadThread: Invalid record name for upload: %s"%name

		# wait a small amount of time before proceeding..
		time.sleep(emdash.config.get('sleeptime'))

		# Remove the "meta-parameters" used for queue details
		rec = {}
		for k,v in item.items():
			if not k.startswith("_"):
				rec[k] = v												

		# Get the handler and upload
		handler = emdash.handlers.get_handler(rectype=rectype)
		dbt = handler(
			db=self.db, 
			filename=filename,
			name=name, # current upload target (eg. grid_imaging)
			applyparams=rec) # the current EMDash settings

		try:
			rec = dbt.upload()
			rec = self.db.getrecord(rec)

		except Exception, e:
			print "UploadThread exception:", e
			self.signal_file_failure.emit(filename, unicode(e))
			self.queue.put(item)
			time.sleep(5)
		
		else:
			self.signal_file_success.emit(filename, rec)

		self.queue.task_done()



class DownloadThread(UploadThread):
	def action(self):
		item = self.queue.get()	
		dbt = emdash.handlers.AutoHandler(db=self.db)

		try:
			dbt.download_bdo(item)
		except Exception, e:
			print "DownloadThread exception:", e
			self.signal_file_failure.emit(filename, unicode(e))
			self.queue.put(item)
			time.sleep(5)
			
		self.queue.task_done()


__version__ = "$Revision: 1.15 $".split(":")[1][:-1].strip()

