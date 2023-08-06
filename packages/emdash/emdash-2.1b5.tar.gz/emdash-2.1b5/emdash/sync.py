# import os
# import glob
# import optparse
# import re
# import sys
# import time
# 
# import emdash.config
# import emdash.proxy
# import emdash.handlers
# 
# class SyncController(emdash.controller.EMEN2ClientController):
# 
# 	def add_option(self):
# 
# 		self.parser.add_option("--check", action="store_true", help="Do not upload anything; just check file mappings")
# 		self.parser.add_option("--ctf", action="store_true", help="Upload CTF Parameters")
# 		self.parser.add_option("--boxes", action="store_true", help="Upload Boxes")
# 		self.parser.add_option("--eman1", action="store_true", help="Look in EMAN1-style files instead of EMAN2 project database")
# 		self.parser.add_option("--ptcls", action="store_true", help="Upload Particle Sets")
# 		self.parser.add_option("--confirm", action="store_true", help="Request confirmation of mappings before proceeding")
# 		self.parser.add_option("--clip_filename", type="string", help="Remove a substr from source filenames to aid matching, e.g. _filt_ptcls")
# 		self.parser.add_option("--match", type="string", help="Restrict particle sets to this substring, e.g. for quick testing")
# 		#self.parser.add_option("--check_boxsize", type="int", help="Check if a micrograph has been shrunk; if box_size < check_boxsize, zoom by box_size / check_boxsize")
# 		self.parser.add_option("--shrink_factor", type="float", help="Specify a shrink factor (e.g. 0.25 if the boxed micrograph was reduced by a factor of 4)", default=1.0)
# 
# 
# 		usage = """%prog sync [options] <project record ID>
# 
# This program will upload CTF parameters, boxes, and particle sets into an EMEN2 database. Because filenames are not always globally unique, you must specify a base project that will be searched for files.
# 
# If run with "--check", it will only test to see if it can make the correct file mappings between the local EMAN2 project and the remote database. Nothing will be written. This is a good way to test to see if the correct mappings can be made before you attempt to commit any changes.
# 
# 		"""
# 
# 		self.parser.set_usage(usage)
# 
# 
# 	def check_args(self):
# 		try:
# 			self.project = int(self.args[0])
# 		except:
# 			raise Exception, "Project record ID required"
# 
# 
# 		# EMAN2 Support
# 		try:
# 			import EMAN2
# 			self.EMAN2 = EMAN2
# 		except ImportError:
# 			EMAN2 = None
# 
# 
# 		if self.EMAN2 == None:
# 			raise Exception, "EMAN2 support is required"
# 
# 		if self.options.clip_filename:
# 			# print "Debug: Clipping '%s' from filenames"%self.options.clip_filename
# 			test = "filename_ok_filt.mrc"
# 			test_clip = test.replace(self.options.clip_filename or '', "")
# 			# print "\t%s -> %s"%(test, test_clip)
# 
# 
# 
# 	def run(self):
# 
# 		self.source_bdo = {} # map source name to BDO ID
# 		self.source_ctf = {} # CTF for a source
# 		self.source_boxes = {} # Boxes for a source
# 		self.source_box_size = {} # Box size for a source
# 		self.source_quality = {} # assess_image_quality for a source
# 
# 		self.tmpdirs = []
# 		self.projrecs = []
# 
# 		# Check arguments and auth
# 		self.check_args()
# 		self.login()
# 
# 		# Check project and get remote records
# 		self.getremoteinfo()
# 
# 		# Actually read EMAN1 or EMAN2 CTF/boxes
# 		if self.options.eman1:
# 			self.readEMAN1()
# 		else:
# 			self.readEMAN2()
# 			
# 			
# 		# Upload
# 		if self.options.ctf:
# 			self.uploadctf()
# 
# 		if self.options.boxes:
# 			self.uploadboxes()
# 
# 		if self.options.ptcls:
# 			self.uploadptcls()
# 
# 		self.cleanup()
# 
# 
# 	def cleanup(self):
# 		if not self.tmpdirs:
# 			return
# 
# 		print "You will want to remove the following tmp directories. They are not automatically removed to prevent accidental file loss in the event of a bug or other error."
# 		for k in self.tmpdirs:
# 			print "Removing:", k
# 
# 
# 
# 	def readEMAN1(self):
# 		pass
# 		# if self.options.ctf:
# 		# 	self.readEMAN1ctf()
# 		# if self.options.boxes:
# 		# 	self.readEMAN1boxes()
# 
# 
# 
# 	def readEMAN1ctf(self):
# 		try:
# 			f = open("ctfparm.txt", "r")
# 			r = [i.strip() for i in f.readlines()]
# 			f.close()
# 		except:
# 			print "No ctfparm.txt present; could not load EMAN1 CTF parameters"
# 			return
# 
# 		indexes = {
# 			"ctf_defocus_measured": 0, # multiply by -1
# 			"ctf_bfactor": 3,
# 			"tem_voltage": 10,
# 			"aberration_spherical": 11,
# 			"angstroms_per_pixel": 12,
# 			"ctf_astig_angle": 2 ,
# 			"ctf_astig_defocus_diff": 1,
# 			"ctf_ampcont": 5, # multiply by 100
# 		}
# 
# 		for i in r:
# 			try:
# 				source, params = i.split("\t")
# 				params = params.split(",")
# 
# 				# it seems that if there are 14 params, astig params are inserted as 1,2
# 				shift = 0
# 				if len(params) == 14:
# 					shift = 2
# 
# 				ctf = self.EMAN2.EMAN2Ctf()
# 				ctf.defocus = float(params[0]) * -1
# 				ctf.bfactor = float(params[1+shift]) * 4 # Convert to Henderson convention
# 				ctf.ampcont = float(params[3+shift]) * 100
# 
# 				# print "defocus %s, bfactor %s, ampcont %s"%(ctf.defocus, ctf.bfactor, ctf.ampcont)
# 				self.source_ctf[source] = ctf
# 			except:
# 				print "Unable to parse CTF parameters, skipping"
# 
# 
# 
# 	def readEMAN1boxes(self):
# 		boxes = glob.glob("*.box")
# 
# 		if not boxes:
# 			print "No EMAN1 .box files found"
# 			return
# 
# 		print "Found EMAN1 boxes: %s"%boxes
# 
# 		for box in boxes:
# 			try:
# 				source = os.path.splitext(box)[0]
# 				box_size, coords = self.readEMAN1box(box)
# 			except:
# 				print "Could not load data from box %s, skipping"%box
# 				continue
# 
# 			self.source_box_size[source] = box_size
# 			self.source_boxes[source] = coords
# 
# 
# 
# 	def readEMAN1box(self, box):
# 		f = open(box, "r")
# 		r = [i.split() for i in f.readlines()]
# 		f.close()
# 
# 		coords = []
# 		for b in r:
# 			box_size = int(b[2])
# 			xc = (int(b[0]) + (box_size/2)) / self.options.shrink_factor
# 			yc = (int(b[1]) + (box_size/2)) / self.options.shrink_factor
# 			coords.append([int(xc),int(yc)])
# 
# 		box_size = int(box_size / self.options.shrink_factor)
# 
# 		return box_size, coords
# 
# 
# 
# 	def readEMAN2(self):
# 
# 		###############
# 		# Find all the raw images, particle sets, and CTF parameters in the local DB
# 		###############
# 
# 		print "\nOpening EMAN2 local project"
# 
# 		projdb = self.EMAN2.db_open_dict("bdb:project")
# 		ptclsets = projdb.get("global.spr_ptcls_dict", {})
# 		e2ctfparms = self.EMAN2.db_open_dict("bdb:e2ctf.parms")
# 		total = len(ptclsets)
# 
# 
# 		# Read the EMAN2 managed particle sets
# 		for count, (k,v) in enumerate(ptclsets.items()):
# 			ref = v.get('Phase flipped-hp') or v.get('Phase flipped') or v.get('Original Data')
# 
# 			if not ref:
# 				print "No particles found for %s, skipping"%k
# 				continue
# 
# 			print "%s of %s: Getting info for particle set %s from %s"%(count+1, total, k, ref)
# 
# 			d = self.EMAN2.db_open_dict(ref)
# 
# 			coords = []
# 			maxrec = d['maxrec']
# 			if maxrec == None:
# 				print "No particles in %s, skipping"%(k)
# 				d.close()
# 				continue
# 
# 			try:
# 				source = os.path.basename(ptcl.get_attr('ptcl_source_image'))
# 			except:
# 				source = k
# 				print "\tUnable to get source image %s, using %s for the filename search"%(k,k)
# 
# 			# Get info from first particle in stack
# 			ptcl = d[0]
# 
# 			###############
# 			# Check remote sources, and write it back to the EMAN2db if necessary
# 			###############
# 			
# 			set_source = False
# 			source_uri = None
# 			try:
# 				source_uri = ptcl.get_attr('source_uri')
# 				print "\tFound existing source_uri: ", source_uri				
# 			except:
# 				matches = self.findbinary(source)
# 				if len(matches) == 1:
# 					source_uri = "%s/bdo/%s"%(self.db._host, matches[0])
# 					set_source = True
# 					print "\tUsing mapped source_uri:", source_uri
# 				else:
# 					print "\tNo source_uri or ambiguous source_uri:", matches
# 
# 			if source_uri:
# 				self.source_bdo[source] = source_uri
# 
# 			if set_source and source_uri:
# 				print "\t... setting source_uri attr", source_uri
# 				for i in range(maxrec+1):
# 					d.set_attr(i, 'source_uri', source_uri)
# 
# 
# 			###########################
# 			# Read CTF / Boxes
# 			###########################
# 
# 			# Try to read boxes from particle headers
# 			if self.options.boxes:
# 				for i in range(maxrec+1):
# 					dptcl = d[i]
# 					try:
# 						x, y = dptcl.get_attr('ptcl_source_coord')
# 						x /= self.options.shrink_factor
# 						y /= self.options.shrink_factor
# 						coords.append([int(x), int(y)])
# 					except:
# 						coords.append(None)
# 
# 
# 				if None in coords:
# 					print "\tSome particles for %s did not specify coordinates"%k
# 					coords = []
# 					# self.options.boxes = False
# 
# 				print "Got box_size %s and coords %s"%(box_size, coords)
# 
# 				if box_size and coords:
# 					self.source_box_size[source] = box_size
# 					self.source_boxes[source] = coords
# 					
# 					
# 
# 			if self.options.ctf:
# 				try: ctf = ptcl.get_attr("ctf")
# 				except: ctf = None
# 
# 				try: box_size = int(ptcl.get_attr("nx") / self.options.shrink_factor)
# 				except: box_size = None								
# 
# 				# Get alternative CTF and quality from e2ctfit settings
# 				ctf2, quality = self.readEMAN2e2ctfparms(e2ctfparms, k)
# 				if not ctf and ctf2:
# 					print "\tUsing CTF parameters from bdb:e2ctf.parms#%s"%k
# 					ctf = ctf2
# 
# 				if ctf:
# 					self.source_ctf[source] = ctf
# 					print "\tGot CTF: defocus %s, B-factor %s"%(ctf.defocus, ctf.bfactor)
# 				else:
# 					print "\tNo CTF for %s"%k
# 
# 				if quality:
# 					self.source_quality[source] = quality
# 
# 
# 
# 			d.close()
# 
# 
# 		# If we can't find any EMAN2 managed particle sets, at least check e2ctf.parms for any CTF params
# 		# if not ptclsets:
# 		# 	print "No EMAN2 managed particle sets found; checking e2ctf.parms for CTF instead"
# 		# 	# self.options.boxes = False
# 		# 
# 		# 	for k,v in e2ctfparms.items():
# 		# 		ctf, quality = self.readEMAN2e2ctfparms(e2ctfparms, k)
# 		# 		source = k.split("_ptcl")[0]
# 		# 
# 		# 		if ctf:
# 		# 			self.source_ctf[source] = ctf
# 		# 		if quality:
# 		# 			self.source_quality[source] = quality
# 
# 
# 		print "\n%s Files in local project: "%len(self.source_ctf), self.source_ctf.keys()
# 
# 		projdb.close()
# 		e2ctfparms.close()
# 
# 
# 
# 	def readEMAN2e2ctfparms(self, e2ctfparms, item):
# 		ctf2 = None
# 		quality = None
# 
# 		ctf_str = e2ctfparms.get(item)
# 		if ctf_str:
# 			try:
# 				ctf2 = self.EMAN2.EMAN2Ctf()
# 				ctf2.from_string(ctf_str[0])
# 				quality = ctf_str[-1]
# 			except:
# 				print "\tProblem reading CTF from bdb:e2ctf.parms for %s"%item
# 
# 		return ctf2, quality
# 
# 
# 
# 	def _filematch(self, i, j):
# 		if i.lower() in j.lower(): return True
# 
# 
# 
# 	def getremoteinfo(self):
# 		# Since filenames are not guaranteed unique, restrict to a project...
# 		print "\nChecking project %s on %s"%(self.project, self.db._host)
# 
# 		self.projrecs = self.db.getchildren(self.project, -1, ["ccd","scan"])
# 		print "\tFound %s ccds/scans in remote project"%len(self.projrecs)
# 
# 		bdos = self.db.getbinary(self.projrecs)
# 		print "\tFound %s binaries"%len(bdos)
# 
# 		# Semi-private attr.. calculate these to use in findbinary
# 		self.bdosbyname = dict([[i["name"], i] for i in bdos])
# 		self.bdosbyfilename = dict([[i["filename"], i["name"]] for i in bdos])
# 
# 
# 
# 	def findbinary(self, source):
# 		# For each file in the local project, search for a matching BDO and record ID in the database
# 
# 		q = source.replace(self.options.clip_filename or '', '')
# 		gzipstrip = ".gz" in source
# 
# 		# ian: replace this with functools.partial
# 		# matches = map(bdosbyfilename.get, filter(lambda x:q in x.split("."), filenames))
# 		matches = []
# 		for i in self.bdosbyfilename.keys():
# 			i2 = i
# 			if gzipstrip:
# 				i2 = i.replace('.gz','')
# 			if self._filematch(q, i2):
# 				matches.append(self.bdosbyfilename.get(i))
# 
# 		return matches
# 
# 
# 
# 	def getbdo(self, source):
# 		source_uri = self.source_bdo.get(source)
# 		if not source_uri:
# 			return None
# 			
# 		bdoid = source_uri.split("/")[-1]
# 		match = self.bdosbyname.get(bdoid)
# 		if not match:
# 			match = self.db.getbinary(match)
# 			self.bdosbyname[bdoid] = match
# 			
# 		return match
# 
# 
# 
# 	def uploadctf(self):
# 
# 		###############
# 		# Now that we have found all source images, CTF parameters, and database references, prepare to save in DB.
# 		###############
# 
# 		for source, ctf in self.source_ctf.items():
# 			bdo = self.getbdo(source)
# 			quality = self.source_quality.get(source)
# 
# 			if not bdo:
# 				print "No BDO found for %s"%source
# 				continue
# 
# 			if not ctf:
# 				print "No CTF found for %s"%source
# 				continue
# 
# 			rec = self.db.getrecord(bdo.get('name'))
# 
# 			if rec.get("ctf_defocus_measured") == ctf.defocus and rec.get("ctf_bfactor") == ctf.bfactor and rec.get("ctf_ampcont") == ctf.ampcont and rec.get("assess_image_quality") == quality:
# 				print "%s already has current CTF parameters"%source
# 				continue
# 
# 			rec["ctf_defocus_measured"] = ctf.defocus
# 			rec["ctf_bfactor"] = ctf.bfactor
# 			rec["ctf_ampcont"] = ctf.ampcont
# 
# 			if quality != None:
# 				rec["assess_image_quality"] = quality
# 
# 			putrecs.append(rec)
# 
# 		###############
# 		# Store / upload
# 		###############
# 
# 		print "\nCommitting %s updated records with changed CTF..."%(len(putrecs))
# 
# 		self.db.putrecord(putrecs)
# 
# 
# 
# 	def uploadboxes(self):
# 		
# 		print "\nPreparing to upload boxes..."
# 		newboxes = []
# 
# 		for source, boxes in self.source_boxes.items():
# 
# 			bdo = self.getbdo(source)
# 			box_size = self.source_box_size[source]
# 
# 			if not bdo:
# 				print "\tNo BDO for %s"%source
# 				continue
# 
# 			name = bdo.get("record")
# 
# 			# Check remote site for existing boxes
# 			remoteboxes = self.db.getchildren(name, -1, ["box"])
# 
# 			if len(remoteboxes) == 1:
# 				print "\tUpdating existing box record"
# 				newbox = self.db.getrecord(remoteboxes.pop())
# 
# 			else:
# 				if len(remoteboxes) > 1:
# 					print "\tNote: more than one box record already specified!"
# 
# 				print "\tCreating new box record"
# 				newbox = self.db.newrecord("box", name)
# 
# 			print "\t%s / %s has %s boxes with box size %s"%(source, name, len(boxes), box_size)
# 
# 			newbox["box_coords"] = boxes
# 			newbox["box_size"] = box_size
# 
# 			newboxes.append(newbox)
# 
# 
# 		print "\tCommitting %s box records"%(len(newboxes))
# 		newrecs = self.db.putrecord(newboxes)
# 		# print "\t... %s"%", ".join([i.get('name') for i in newrecs])
# 
# 
# 
# 	def uploadptcls(self):
# 
# 		print "\nUploading particles..."
# 
# 		print "Not implemented yet"
# 
# 		for source in self.source_ctf.keys():
# 			pass
