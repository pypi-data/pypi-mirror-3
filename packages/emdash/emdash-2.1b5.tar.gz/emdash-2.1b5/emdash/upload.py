# $Id: upload.py,v 1.59 2012/02/17 10:26:50 irees Exp $
import Queue
import collections
import datetime
import functools
import getpass
import glob
import operator
import optparse
import os
import re
import sys
import time
import json

# PyQt4 imports
from PyQt4 import QtGui, QtCore, Qt

# emdash imports
import emdash.config
import emdash.emmodels
import emdash.emwizard
import emdash.emthreads
import emdash.ui

def main():
	parser = emdash.config.DBRPCOptions()
	usage = """%prog"""
	parser.set_usage(usage)	

	parser.add_option("--type", "-t", type="string",  help="Session type. Available: base, microscopy, scan")

	mgroup = optparse.OptionGroup(parser, "Microscopy Session Options")
	mgroup.add_option("--microscope", "-m", type="int",  help="Microscope or Microscope folder Record name (e.g. 110, 114..)")
	mgroup.add_option("--session_rectype","-s", type="string", help="Session Protocol (Default is microscopy)", default='microscopy')
	parser.add_option_group(mgroup)

	sgroup = optparse.OptionGroup(parser, "Scan Conversion Options")
	sgroup.add_option("--tif2mrc", metavar="<0|1>", dest="tif2mrc", type="int", help="Scan Option: See nikontiff2mrc for options and defaults for the following options:", default=True)		
	sgroup.add_option("--bin", metavar="<n>", dest="bin", type="float", help="Scan Option: bin the pixels. default to 1 (no binning)")	
	sgroup.add_option("--invert", metavar="<0|1>", dest="invert", type="int", help="Scan Option: invert the contrast to make particles white. default to 0")	
	sgroup.add_option("--ODconversion", metavar="<0|1>", dest="odconversion", type="int",  help="Scan Option: if convert pixel value from transmitted light intensity to O.D. of the film. enabled by default")
	parser.add_option_group(sgroup)

	(options, args) = parser.parse_args()
	db = parser.opendb()

	if options.type == 'microscopy':
		appclass = MicroscopeUpload
	elif options.type == 'scan':
		appclass = ScanUpload
	else:
		appclass = BaseUpload


	emdash.config.set('microscope', options.microscope)
	emdash.config.set('session_rectype', options.session_rectype)

	app = QtGui.QApplication(sys.argv)
	window = appclass(db=db)
	window.request_login()
	sys.exit(app.exec_())	
	
	
	
##############################
# Some dialogs: Warning, Login, ...
##############################


def confirm(parent=None, title='Confirm', text=''):
	reply = QtGui.QMessageBox.question(
		parent, 
		title,
		text, 
		QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
		QtGui.QMessageBox.No
		)

	if reply == QtGui.QMessageBox.Yes:
		return True
	else:
		return False



class DWarning(QtGui.QDialog):
	def __init__(self, displayname=None, session=None, parent=None):
		QtGui.QDialog.__init__(self, parent=parent)		
		self.ui = emdash.ui.Ui_Warning.Ui_Warning()
		self.ui.setupUi(self)
		self.ui.label_user.setText(unicode(displayname))
		self.ui.label_session.setText("""<a href="%s/record/%s/">%s</a>"""%(emdash.config.get('host'), session, session))

	def closeEvent(self, event):
		event.ignore()




class Login(QtGui.QDialog):

	signal_trylogin = QtCore.pyqtSignal(unicode, unicode)	

	def __init__(self, name=None, password=None, authmsg=None, microscope=None, parent=None):
		QtGui.QDialog.__init__(self, parent=parent)		
		self.ui = emdash.ui.Ui_Login.Ui_Login()
		self.ui.setupUi(self)

		if authmsg:
			self.ui.label_login.setText(authmsg)
		else:
			self.ui.label_login.setText('Login: %s'%emdash.config.get('host'))			

		if name:
			self.ui.edit_name.setText(name)

		if password:
			self.ui.edit_password.setText(password)

		#if microscope:
		#	self.ui.edit_microscope.setText(str(microscope))
		# self.ui.edit_host.setText(emdash.config.get('host'))


	@QtCore.pyqtSlot(unicode)
	def ok(self, ctxid):
		self.done(0)


	@QtCore.pyqtSlot(unicode)
	def error(self, e):
		self.ui.label_login.setText(e)


	# turn on before deployment..
	def accept(self):		
		def int_or_none(value):
			if value:
				return int(value)
			return None

		if not self.ui.edit_name.text():
			return

		# host = self.ui.edit_host.text()
		# emdash.config.set('host', unicode(host))
		# microscope = self.ui.edit_microscope.text()
		# emdash.config.set('microscope', int_or_none(microscope))
		# if not emdash.config.get('host'):
		#	msg = "No EMEN2 server specified!"
		#	self.error(msg)
		#	return
		# if not emdash.config.get('microscope'):
		# 	msg = "No microscope specified!"
		# 	self.error(msg)
		# 	return

		self.ui.label_login.setText("Logging in...")
		
		self.signal_trylogin.emit(
			unicode(self.ui.edit_name.text()),
			unicode(self.ui.edit_password.text()))	

		self.ui.edit_password.clear()


##############################
# Base EMDash Uploader
##############################

class BaseTransport(QtGui.QMainWindow):
	# Base class for an Upload UI
	ui = emdash.ui.Ui_Upload.Ui_Upload
	worker = emdash.emthreads.UploadThread
	
	# Session controls
	signal_begin_session = QtCore.pyqtSignal()
	signal_end_session = QtCore.pyqtSignal()
	signal_target = QtCore.pyqtSignal(int)

	# Updated record
	signal_file_status = QtCore.pyqtSignal(unicode, object)
	signal_exception = QtCore.pyqtSignal(unicode)
	
	# Files
	signal_setpath = QtCore.pyqtSignal(unicode)
	signal_newfile = QtCore.pyqtSignal(unicode, object)

	# Login
	signal_login = QtCore.pyqtSignal(unicode)
	signal_login_exception = QtCore.pyqtSignal(unicode)
	signal_logout = QtCore.pyqtSignal()
	
	headers = ["_recname", "_status"]
	headernames = ["Name", "Status"]
	headerwidths = [400,200]

	def __init__(self, parent=None, db=None):
		super(BaseTransport, self).__init__(parent=parent)

		# File / queue
		self.path = None		
		self.end = False		

		# Get a DBProxy handle
		self.db = db			

		# Current targets
		self.names = {}
		self.target = None
		
		# Cache
		self.user = {}
		self.recs = {}
		self.recnames = {}
				
		###################
		# Queue
		self.queuemodel = emdash.emmodels.QueueModel(
			parent=self, 
			headers=self.headers, 
			headernames=self.headernames)
		
		
		###################
		# Setup UI
		self.ui = self.ui()
		self.ui.setupUi(self)
		
		
		###################
		# Worker threads
		
		# Starts when a new session is made
		self.clockthread = emdash.emthreads.ClockThread()
		self.clockthread.signal_tick.connect(self.tock, type=QtCore.Qt.QueuedConnection)
		self.signal_begin_session.connect(self.clockthread.start, type=QtCore.Qt.QueuedConnection)

		# FSPollThread starts whenever a directory is selected
		self.fspollthread = emdash.emthreads.FSPollThread()

		# Send any updates to the queue model/view
		self.worker = self.worker(db=emdash.config.copydb(self.db), queue=self.queuemodel.queue)
		self.worker.signal_file_status.connect(self.queuemodel.file_status, type=QtCore.Qt.QueuedConnection)
		self.worker.signal_file_success.connect(self.queuemodel.file_success, type=QtCore.Qt.QueuedConnection)
		self.worker.signal_file_failure.connect(self.queuemodel.file_failure, type=QtCore.Qt.QueuedConnection)

		self.signal_login.connect(self.worker.login_cb, type=QtCore.Qt.QueuedConnection)
		self.signal_file_status.connect(self.queuemodel.file_status, type=QtCore.Qt.QueuedConnection)

		# New upload target
		self.signal_target.connect(self.queuemodel.target, type=QtCore.Qt.QueuedConnection)
		self.signal_target.connect(self.worker.start, type=QtCore.Qt.QueuedConnection)

		# New file
		# self.signal_newfile.connect(self.queuemodel.newfile, type=QtCore.Qt.QueuedConnection)
		self.fspollthread.signal_newfile.connect(self.queuemodel.newfile, type=QtCore.Qt.QueuedConnection)
		self.fspollthread.signal_newfile.connect(self.ui.tree_files.newfile, type=QtCore.Qt.QueuedConnection)

		self.signal_setpath.connect(self.fspollthread.setpath, type=QtCore.Qt.QueuedConnection)
		self.signal_setpath.connect(self.fspollthread.start, type=QtCore.Qt.QueuedConnection)

		############
		# UI
		self.ui.button_session.addAction(QtGui.QAction("Logout", self, triggered=self.close))

		# File control widget
		self.ui.tree_files.signal_set.connect(self.set, type=QtCore.Qt.QueuedConnection)
		self.ui.tree_files.signal_enqueue.connect(self.worker.enqueue, type=QtCore.Qt.QueuedConnection)	
		self.ui.tree_files.prog_column(len(self.headers)-1)

		self.signal_login.connect(self.login_cb, type=QtCore.Qt.QueuedConnection)
		
		self.ui.tree_files.setModel(self.queuemodel)
		for count, width in enumerate(self.headerwidths or []):
			self.ui.tree_files.setColumnWidth(count, width)
		
		self.init()


	def init(self):
		pass


	@QtCore.pyqtSlot()
	def update_ui(self):
		"""Update the current set of records."""
		rnget = filter(None, self.names.values())

		if self.target:
			rnget.append(self.target)
		
		try:
			recs = self.db.getrecord(rnget)
		except Exception, e:
			print "Couldn't get records: ", e
		else:
			for rec in recs:
				self.recs[rec.get('name')] = rec

		try:
			rn = self.db.renderview(rnget)
		except Exception, e:
			print "Couldn't get rendered views: ", e
		else:
			self.recnames.update(rn)

		if self.target:
			ready = True
		else:
			ready = False
			
		try:	
			self.ui.button_path.setEnabled(ready)
		except:
			pass
		try:
			self.ui.label_grid.setText(self.getlabel(name=self.target))		
		except:
			pass
			


	@QtCore.pyqtSlot(str)
	def error(self, e):
		error = QtGui.QMessageBox(parent=self)
		error.setWindowTitle("Error")
		error.setText(unicode(e))
		error.setIcon(QtGui.QMessageBox.Critical)
		error.exec_()



	###############################
	# Editing records / Comments
	###############################

	@QtCore.pyqtSlot(int, unicode, unicode)
	def set(self, name, param, value):
		# print "Setting:", name, param, value
		if name < 0:
			self.signal_exception.emit("Cannot update non-existent record")
			return		

		try:
			rec = self.db.putrecordvalues(name, {unicode(param): unicode(value)})
		except Exception, inst:
			self.signal_exception.emit("Cannot update record: %s"%inst)
		else:
			if rec:
				self.signal_file_status.emit(unicode(rec.get('name')), rec)

		if param == 'comments':
			self.update_comments()
			

	@QtCore.pyqtSlot()
	def update_comments(self):
		pass


	@QtCore.pyqtSlot(object, object)
	def edit_records(self, editrecords, selectrecords):		
		try:
			updrecs = self.db.putrecord(editrecords)
		except Exception, e:
			self.signal_exception.emit(unicode(e))
			return

		self.names.update(selectrecords or {})
		for rec in updrecs:
			self.recs[rec.get('name')] = rec
			self.names[rec.get('rectype')] = rec.get('name')
			self.signal_file_status.emit(unicode(rec.get('name')), rec)
			
		# this is an ugly hack
		self._check_target()	
		
		# Update the UI	
		self.update_ui()


	@QtCore.pyqtSlot(int)
	def set_target(self, name):
		try:
			rec = self.db.getrecord(name)
		except Exception, e:
			self.signal_exception.emit(unicode(e))
			return

		self.target = rec.get('name')
		self.recs[rec.get('name')] = rec
		self.signal_file_status.emit(unicode(rec.get('name')), rec)
		self.signal_target.emit(self.target)
		self.update_ui()


	def _check_target(self):
		return




	##############################
	# Session Management
	##############################

	def request_login(self, authmsg=None, name=None, password=None, microscope=None):
		# Get login info for new session
		name = name or emdash.config.get('name')
		password = password or emdash.config.get('password')		
		microscope = microscope or emdash.config.get('microscope')
		l = Login(parent=self, authmsg=authmsg, name=name, password=password, microscope=microscope)
		l.signal_trylogin.connect(self.login)
		self.signal_login.connect(l.ok)
		self.signal_login_exception.connect(l.error)
		l.show()


	@QtCore.pyqtSlot(unicode, unicode)
	def login(self, name=None, password=None):
		# Attempt to login	
		self.db._setContext(None)
		try:
			self.db.login(unicode(name), unicode(password))
		except Exception, e:
			self.signal_login_exception.emit(unicode(e))
			return

		# Get our user details (display name, bookmarks, etc.)
	 	name = self.db.checkcontext()[0]
		self.user = self.db.getuser(name)
		self.ui.label_user.setText(self.user.get('displayname'))
		self.show()
		
		# Login callbacks
		self.signal_login.emit(self.db._ctx.ctxid)
		
		
	@QtCore.pyqtSlot(unicode)
	def login_cb(self, ctxid):
		self.begin_session()


	@QtCore.pyqtSlot()
	def begin_session(self):
		self.signal_begin_session.emit()
		self.update_ui()
		self.show()
		

	@QtCore.pyqtSlot()	
	def end_session(self):
		self.close()
	

	@QtCore.pyqtSlot(str)	
	def tock(self, t):
		# Update session clock
		target = self.names.get(emdash.config.get('session_rectype'))
		if t == None:
			t = ""
		elif target > -1:
			t = """<a href="%s/record/%s/?ctxid=%s">%s</a>"""%(emdash.config.get('host'), target, self.db._ctx.ctxid, t)	
		else:
			t = """<a href="%s?ctxid=%s">%s</a>"""%(emdash.config.get('host'), self.db._ctx.ctxid, t)	
		self.ui.label_session.setText(t)


	#####################
	# Event handlers
	#####################
	
	def closeEvent(self, event):
		accept = confirm(parent=self, title="Logout", text="Are you sure you want to logout? Any pending transfers will be cancelled.")
		if accept:
			self.end_session()
			event.accept()
		else:
			event.ignore()
		

	#####################
	# Base Wizards
	#####################

	@QtCore.pyqtSlot()
	def _select_target_wizard(self):
		wizard = emdash.emwizard.SelectAnyWizard(parent=self, selected=self.names, db=emdash.config.copydb(self.db))
		wizard.signal_any.connect(self.set_target, type=QtCore.Qt.QueuedConnection)
		wizard.exec_()
				
				
	@QtCore.pyqtSlot()
	def _name_target_wizard(self):
		d = QtGui.QInputDialog(self)
		d.setLabelText("Record Name")
		d.setIntMaximum(2147483647)
		d.setIntMinimum(0)
		d.setInputMode(QtGui.QInputDialog.IntInput)
		d.intValueSelected.connect(self.set_target, type=QtCore.Qt.QueuedConnection)
		d.exec_()

		
	#####################
	# Misc.
	#####################
			
	def getlabel(self, name=None, rectypes=None):
		"""return the name/recname link for the first rectype found"""
		
		if not name:
			if not hasattr(rectypes, "__iter__"):
				rectypes = [rectypes]
			for r in rectypes:
				if self.names.get(r) != None:
					name = self.names.get(r)

		if name:
			return """<a href="%s/record/%s?ctxid=%s">%s</a>"""%(emdash.config.get('host'), name, self.db._ctx.ctxid, self.recnames.get(str(name), name))

		return ""


	def connect_slider(self, i, factor=1000.0):
		slider = getattr(self.ui, 'slider_%s'%i)
		edit = getattr(self.ui, 'edit_%s'%i)
		slider.sliderMoved.connect(functools.partial(self._slider_to_edit, target=edit, factor=factor), type=QtCore.Qt.QueuedConnection)
		edit.textChanged.connect(functools.partial(self._edit_to_slider, target=slider, factor=factor), type=QtCore.Qt.QueuedConnection)
		edit.textChanged.connect(functools.partial(self.queuemodel.set_setting, param=i), type=QtCore.Qt.QueuedConnection)		


	def _slider_to_edit(self, i, target=None, factor=1.0):
		try:
			i = i / factor
		except:
			i = 0
		target.setText(str(i))


	def _edit_to_slider(self, i, target=None, factor=1.0):
		try:
			i = float(i) * factor
		except:
			i = 0
		target.setValue(int(float(i or 0)))	








class BaseUpload(BaseTransport):

	def init(self):
		self.ui.button_path.addAction(QtGui.QAction("Select directory", self, triggered=self._setpath))		
		self.ui.button_path.addAction(QtGui.QAction("Add files", self, triggered=self._addfiles))
		self.ui.button_grid.addAction(QtGui.QAction("Browse for destination", self, triggered=self._select_target_wizard))
		self.ui.button_grid.addAction(QtGui.QAction("Manually select destination", self, triggered=self._name_target_wizard))


	#####################
	# Comments
	#####################

	@QtCore.pyqtSlot(unicode)
	def addcomment(self, rectype):
		# Add a comment to a known record
		comment = self.ui.edit_addcomment.toPlainText()	

		name = self.names.get(rectype, -1)
		if name < 0:
			self.error("Could not add comment because there was no %s record yet for this session."%rectype)
			return

		self.ui.button_addcomment.setEnabled(False)
		self.ui.edit_addcomment.setEnabled(False)
		self.set(name, "comments", comment)


	#####################
	# Signals to FS Poll Thread
	#####################

	@QtCore.pyqtSlot()
	def _addfiles(self):
		# Select directory to watch for queue
		d = QtGui.QFileDialog(self)
		d.setFileMode(QtGui.QFileDialog.ExistingFiles)
		d.filesSelected.connect(self.fspollthread.newfiles, type=QtCore.Qt.QueuedConnection)
		d.filesSelected.connect(self.fspollthread.start, type=QtCore.Qt.QueuedConnection)				
		d.exec_()


	@QtCore.pyqtSlot()
	def _setpath(self):
		# Select directory to watch for queue
		d = QtGui.QFileDialog(self)
		d.setFileMode(QtGui.QFileDialog.Directory)
		d.fileSelected.connect(self.check_path, type=QtCore.Qt.QueuedConnection)
		d.exec_()


	@QtCore.pyqtSlot(unicode)
	def check_path(self, path):
		print "Checking path:", path
		handler = emdash.handlers.AutoHandler()
		found = {}
		for f in handler.poll(path, seen=set()):
			print "Found", f
			jsonfile = '%s.json'%f
			data = {}
			if os.path.exists(jsonfile):
				data = json.load(file(jsonfile,"r")) or {}
				print "... already uploaded to record:", data.get('record')
				found[f] = data.get('record')				
	
		if found:
			text = 'Found %s files that have already been uploaded (see console for details.) These files will be skipped and not uploaded again. To re-upload these files, remove the json files to clear the references.\n\nContinue?'%len(found)
			accept = confirm(parent=self, title="Warning", text=text)
		else:
			accept = True

		if accept:
			self.update_path(path)
				


	@QtCore.pyqtSlot(unicode)
	def update_path(self, path):
		self.ui.label_path.setText(unicode(path))
		self.signal_setpath.emit(unicode(path))



################################
# Microscope Upload
################################


class MicroscopeUpload(BaseUpload):

	ui = emdash.ui.Ui_MicroscopeUpload.Ui_Upload
	headers = ["_recname", "tem_magnification_set", "ctf_defocus_set", 'tem_dose_rate', 'time_exposure_tem', "assess_image_quality", "_status"]
	headernames = ["Name", "Mag", "Defocus", "Dose", "Exposure", "Quality", "Status"]
	headerwidths = [250, 60, 60, 60, 60, 80, 50]

	def init(self):
		# Defaults..
		self.ui.button_path.addAction(QtGui.QAction("Select directory", self, triggered=self._setpath))		
		self.ui.button_path.addAction(QtGui.QAction("Add files", self, triggered=self._addfiles))

		# Comments
		self.ui.button_addcomment.addAction(QtGui.QAction("this grid", self, triggered=functools.partial(self.addcomment, rectype='grid_imaging')))
		self.ui.button_addcomment.addAction(QtGui.QAction("this microscopy session", self, triggered=functools.partial(self.addcomment, rectype='microscopy')))
		self.ui.button_addcomment.addAction(QtGui.QAction("this microscope", self, triggered=functools.partial(self.addcomment, rectype='microscope')))			
	
		# More Drop-down buttons
		self.ui.button_grid.addAction(QtGui.QAction("New grid imaging session", self, triggered=self._newgrid_wizard))
		self.ui.button_grid.addAction(QtGui.QAction("New freezing session", self, triggered=self._newfreezing_wizard))
		self.ui.button_grid.addAction(QtGui.QAction("Edit grid imaging session details", self, triggered=self._edit_grid_wizard))
		self.ui.button_grid.addAction(QtGui.QAction("Browse for existing grid imaging session", self, triggered=self._select_grid_wizard))

		self.ui.button_grid.addAction(QtGui.QAction("Browse for destination", self, triggered=self._select_target_wizard))
		self.ui.button_grid.addAction(QtGui.QAction("Manually select destination", self, triggered=self._name_target_wizard))

		# Session
		# self.ui.button_session.addAction(QtGui.QAction("Edit session", self, triggered=self._edit_microscopy_wizard))
		self.ui.button_session.addAction(QtGui.QAction("Select existing session", self, triggered=self._name_microscopy_wizard))		

		# New Micrograph
		# self.ui.button_newmicrograph.clicked.connect(self.newmicrograph, type=QtCore.Qt.QueuedConnection)			
	
		# Editables
		self.connect_slider('tem_magnification_set', factor=1.0)
		self.connect_slider('ctf_defocus_set')
		self.connect_slider('tem_dose_rate')
		self.connect_slider('time_exposure_tem')
		
		self.ui.edit_id_micrograph.textChanged.connect(functools.partial(self.queuemodel.set_setting, param='id_micrograph'), type=QtCore.Qt.QueuedConnection)
		self.ui.button_assess_ice_comments.clicked.connect(self._assess_ice_comments, type=QtCore.Qt.QueuedConnection)
		self.ui.button_assess_ice_thick.clicked.connect(self._assess_ice_thick, type=QtCore.Qt.QueuedConnection)

		self.ui.tree_files.star_column(len(self.headers)-2)


	def _check_target(self):
		# Set the target if a wizard returns a grid_imaging record...		
		grid = self.names.get('grid_imaging')
		if grid is not None:
			self.set_target(grid)


	@QtCore.pyqtSlot(unicode)
	def login_cb(self, ctxid):
		# This wizard will call begin_Session
		self._newmicroscopy_wizard()


	@QtCore.pyqtSlot()
	def update_ui(self):
		super(MicroscopeUpload, self).update_ui()

		self.ui.frame_settings.setEnabled(self.ui.button_path.isEnabled())
		self.ui.button_newmicrograph.setEnabled(self.ui.button_path.isEnabled())
			
	
		# Update the UI to reflect these selected records
		self.ui.label_project.setText(self.getlabel(rectypes=["project","subproject"]))
		self.ui.label_freeze.setText(self.getlabel(rectypes=["grid_preparation"]))
	
		gir = self.recs.get(self.target, dict())
		if gir.get('tem_magnification_set') != None:
			self.ui.edit_tem_magnification_set.setText(str(gir.get('tem_magnification_set')))
		if gir.get('ctf_defocus_set') != None:
			self.ui.edit_ctf_defocus_set.setText(str(gir.get('ctf_defocus_set')))
		if gir.get('time_exposure_tem') != None:
			self.ui.edit_time_exposure_tem.setText(str(gir.get('time_exposure_tem')))
		if gir.get('tem_dose_rate') != None:
			self.ui.edit_tem_dose_rate.setText(str(gir.get('tem_dose_rate')))	
	
		film_type = self.recs.get(self.names.get(emdash.config.get('session_rectype')), dict()).get('film_type', '')
		if film_type.lower() in emdash.config.get('film_types'):
			self.ui.edit_id_micrograph.show()
			self.ui.label_newmicrograph.show()
			self.ui.button_newmicrograph.show()			
		else:
			self.ui.edit_id_micrograph.hide()
			self.ui.label_newmicrograph.hide()
			self.ui.button_newmicrograph.hide()		


	# def update_setting(self, param, value):
	# 	try:
	# 		if param == "id_micrograph":
	# 			self.ui.edit_id_micrograph.setText(value)
	# 		elif param == "ctf_defocus_set":
	# 			pass
	# 		elif param == "tem_magnification_set":
	# 			pass
	# 	except:
	# 		pass


	def update_comments(self):
		root = self.names.get('microscope')
		if  root == None:
			return
		
		coms = []
		try:	
			recs = self.db.getchildren(self.names["microscope"], 1, ["microscopy*"])
			coms = self.db.getcomments(recs)			
		except:
			pass
	
		# update the recnames..
		try:
			self.recnames.update(self.db.renderview([i[0] for i in coms], viewtype="recname"))
		except:
			pass
	
		html = []	
		for c in sorted(coms, key=lambda x:x[2], reverse=True):
			t = """<a href="%s/record/%s/?ctxid=%s">%s</a>: %s @ %s: <br /> %s <br /><br />"""%(emdash.config.get('host'), c[0], self.db._ctx.ctxid, self.recnames.get(str(c[0]), c[0]), c[1], c[2], c[3])
			html.append(t)
			
		self.ui.browser_comments.setHtml("".join(html))
		
		# Update...
		self.ui.edit_addcomment.clear()
		self.ui.button_addcomment.setEnabled(True)
		self.ui.edit_addcomment.setEnabled(True)

	
	
	
	##################################
	# Microscope session management
	##################################
	
	@QtCore.pyqtSlot(object, object)
	def begin_session(self, editrecords, selectrecords):	
		# Find the correct microscope
		t = self.db.gettime()
		if emdash.config.get('microscope') == None:
			raise ValueError, "No microscope specified!"

		childrecs = set(self.db.getchildren(emdash.config.get('microscope'), 1, "microscope"))
		childrecs.add(emdash.config.get('microscope'))
		microscopes = self.db.getrecord(list(childrecs))
		microscope = None

		for m in microscopes:
			if m.get('date_start') <= t < m.get('date_end'):
				self.names['microscope'] = m.get('name')

		if not self.names.get('microscope'):
			self.names['microscope'] = emdash.config.get('microscope')
			print "Warnng: No microscope valid for today's date: %s... using %s"%(t, emdash.config.get('microscope'))

		# Use an existing session, or create a new one.
		if selectrecords.get(emdash.config.get('session_rectype')):
			rec = self.db.getrecord(selectrecords.get(emdash.config.get('session_rectype')))

		else:
			rec = self.db.newrecord(emdash.config.get('session_rectype'), self.names.get("microscope"))
			rec["date_start"] = self.db.gettime()
			rec["parents"] = [self.names.get("microscope")]
			rec.update(editrecords[0])
			rec = self.db.putrecord(rec)

		# Update the targets
		self.names[emdash.config.get('session_rectype')] = rec.get("name")
 		super(MicroscopeUpload, self).begin_session()
		self.update_comments()
	

	@QtCore.pyqtSlot()
	def end_session(self):
		if self.names.get(emdash.config.get('session_rectype')) != None:
			try:
				rec = self.db.getrecord(self.names.get(emdash.config.get('session_rectype')))
				rec["date_end"] = self.db.gettime()
				rec = self.db.putrecord(rec)
			except:
				print "Error ending session"

		super(MicroscopeUpload, self).end_session()
		
		
	###############################
	# Some controller specific behaviors...
	###############################

	# Fold this into something else..
	# def newmicrograph(self):
	# 	id_micrograph = self.settings.get('id_micrograph','')
	# 	matches = re.search('(\w+?)(\d+)', id_micrograph)
	# 	if not matches:
	# 		print "Error creating new micrograph: No Micrograph ID..."
	# 		return
	# 
	# 	matches = matches.groups()		
	# 	newid = int(matches[1])+1
	# 	newid = matches[0] + str(newid).zfill(len(matches[1]))
	# 
	# 	data = {'_recname': id_micrograph, '_filename':id_micrograph, 'id_micrograph':id_micrograph, "_auto":True, 'rectype':'micrograph'}
	# 	data.update(self.settings)
	# 
	# 	# Emit the new file signal, and update the UI to show the new file micrograph ID
	# 	self.signal_newfile.emit(id_micrograph, data)
	# 	self.set_setting('id_micrograph', newid)

	
	######################
	# Wizards!!
	######################
	
	@QtCore.pyqtSlot()
	def _newmicroscopy_wizard(self):
		wizard = emdash.emwizard.NewMicroscopyWizard(parent=self, selected=self.names, db=emdash.config.copydb(self.db))
		wizard.signal_done.connect(self.begin_session, type=QtCore.Qt.QueuedConnection)
		wizard.exec_()
	

	@QtCore.pyqtSlot()
	def _name_microscopy_wizard(self):
		d = QtGui.QInputDialog(self)
		d.setLabelText("Microscopy Record ID")
		d.setIntMaximum(2147483647)
		d.setIntMinimum(0)
		d.setInputMode(QtGui.QInputDialog.IntInput)
		d.intValueSelected.connect(self.__select_microscopy, type=QtCore.Qt.QueuedConnection)
		d.exec_()


	@QtCore.pyqtSlot(int)
	def __select_microscopy(self, name):
		self.begin_session([], {emdash.config.get('session_rectype'): int(name)})
	

	@QtCore.pyqtSlot()
	def _edit_microscopy_wizard(self):
		# Edit the microscopy session we just created to fill in details
		wizard = emdash.emwizard.EditMicroscopyWizard(parent=self, selected=self.names, db=emdash.config.copydb(self.db))
		wizard.signal_done.connect(self.edit_records, type=QtCore.Qt.QueuedConnection)
		wizard.exec_()
	
	#########
	
	@QtCore.pyqtSlot()
	def _newfreezing_wizard(self):
		wizard = emdash.emwizard.NewFreezingWizard(parent=self, selected=self.names, db=emdash.config.copydb(self.db))
		wizard.signal_done.connect(self.edit_records, type=QtCore.Qt.QueuedConnection)
		wizard.exec_()


	########		
	# These may return a grid_imaging record,
	# 	which will cause the target to be updated.
	
	@QtCore.pyqtSlot()
	def _newgrid_wizard(self):
		wizard = emdash.emwizard.NewGridWizard(parent=self, selected=self.names, db=emdash.config.copydb(self.db))
		wizard.signal_done.connect(self.edit_records, type=QtCore.Qt.QueuedConnection)
		wizard.exec_()


	@QtCore.pyqtSlot()
	def _edit_grid_wizard(self):
		if self.names.get('grid_imaging') != None:
			wizard = emdash.emwizard.EditGridImagingWizard(parent=self, selected=self.names, db=emdash.config.copydb(self.db))
			wizard.signal_done.connect(self.edit_records, type=QtCore.Qt.QueuedConnection)
			wizard.exec_()
	
	
	#######
	# Manually set target

	@QtCore.pyqtSlot()
	def _select_grid_wizard(self):
		wizard = emdash.emwizard.SelectGridWizard(parent=self, selected=self.names, db=emdash.config.copydb(self.db))
		wizard.signal_done.connect(self.set_target, type=QtCore.Qt.QueuedConnection)
		wizard.exec_()


	#################
	# Comments about ice quality
	#################

	@QtCore.pyqtSlot()
	def _assess_ice_thick(self):
		value = unicode(self.ui.assess_ice_thick.currentText())
		# name = self.names.get("_target", -1)
		name = self.target
		if name < 0:
			self.error("Could not set the ice thickness because you have not yet created a grid imaging session")
			return
		self.set(name, "assess_ice_thick", value)
	
	
	@QtCore.pyqtSlot()		
	def _assess_ice_comments(self):
		value = unicode(self.ui.assess_ice_comments.currentText())
		# name = self.names.get("_target", -1)
		name = self.target
		if name < 0:
			self.error("Could not set the ice conditions because you have not yet created a grid imaging session")
			return
		self.set(name, "assess_ice_comments", value)






# This handler is basically the same as the Microscopy handler, but simpler in a few places.
class ScanUpload(BaseUpload):
	ui = emdash.ui.Ui_ScanUpload.Ui_Upload

	##############################
	# Control handlers...
	#############################
	
	def init(self):		
		# Editables
		self.connect_slider('scan_step')
		self.connect_slider('nikon_gain')
		self.connect_slider('scan_average', factor=10.0)
		self.connect_slider('angstroms_per_pixel')		
	
		self.ui.edit_scanner_film.editTextChanged.connect(functools.partial(self.set_setting, param='scanner_film'), type=QtCore.Qt.QueuedConnection)
		self.ui.edit_scanner_cartridge.editTextChanged.connect(functools.partial(self.set_setting, param='scanner_cartridge'), type=QtCore.Qt.QueuedConnection)
		
		self.ui.button_grid.addAction(QtGui.QAction("Browse for destination", self, triggered=self._select_target_wizard))
		self.ui.button_grid.addAction(QtGui.QAction("Manually select destination", self, triggered=self._name_target_wizard))




if __name__ == '__main__':
	main()




__version__ = "$Revision: 1.59 $".split(":")[1][:-1].strip()
