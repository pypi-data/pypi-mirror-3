import glob
import optparse
import os
import re
import sys
import time

# emdash imports
import emdash.config
import emdash.proxy
import emdash.handlers



def download():
	parser = emdash.config.DBRPCOptions()
	usage = """%prog download [options] <name>"""
	parser.set_usage(usage)
	parser.add_option("--recurse", type="int",help="Recursion level", default=1)
	parser.add_option("--sidecar", "-s", action="store_true", help="Include file with EMEN2 metadata in JSON format")
	parser.add_option("--overwrite", "-o", action="store_true", help="Overwrite existing files (default is to skip)", default=False)
	# parser.add_option("--rename", "-r", action="store_true", help="If a file already exists, save with format 'rename.originalfilename'", default=False)
	# parser.add_option("--bdorename", "-b", action="store_true", help="Rename to 'bdo.YYYYMMDDXXXXX.extension'")
	# parser.add_option("--gzip", action="store_true", dest="compress", help="Decompress gzip'd files. Requires gzip in path (default)", default=True)
	# parser.add_option("--nogzip", action="store_false", dest="compress", help="Do not decompress gzip'd files.")
	(options, args) = parser.parse_args()
	db = parser.opendb(request=True)

	opts = {}
	for k,v in options.__dict__.items():
		opts[k] = v

	for name in args:
		rec = db.getrecord(int(name))
		dbt = emdash.handlers.AutoHandler(db=db, name=name, options=opts)
		dbt.download_find()




def upload():
	parser = emdash.config.DBRPCOptions()
	usage = """%prog upload [options] <record name> <files to upload>"""
	parser.set_usage(usage)
	# parser.add_option("-t", "--rectype", type="str",help="Rectype")
	
	
	(options, args) = parser.parse_args()
	if len(args) < 2:
		parser.error("Record name and files to upload are required")

	name = args[0]
	filenames = args[1:]

	print "%s Files to upload:"%len(filenames)
	for i in filenames:
		print "\t",i

	db = parser.opendb(request=True)
	filecount = len(filenames)
	for count, filename in enumerate(filenames):
		handler = emdash.handlers.get_handler(filename=filename)
		dbt = handler(
			db=db,
			filename=filename,
			name=name
		)
		dbt.upload()
		





#########################
# Ugly console input code
#########################

# def get_param_values(params, db=None):
# 	pds = db.getparamdef(params)
# 	pds = dict([[i.get('name'), i] for i in pds])
# 	
# 	ret = {}
# 	for param in params:
# 		pd = pds.get(param)
# 		ret[param] = get_param_value_console(pd, db=db)
# 	return ret
# 
# 
# 
# def get_param_value_console(param, db=None):
# 	name = param.get('name')
# 
# 	print "\n----- %s -----"%name
# 	print "\tDescription: %s"%param.get('desc_long')
# 	if param.get('defaultunits'):
# 		print "\tUnits: %s"%param.get('defaultunits')
# 
# 
# 	punits = param.get('defaultunits') or ''
# 	lines = None
# 	selections = []
# 
# 	try:
# 		lines = [i[0] for i in db.findvalue(name, '', True, False, 5)]
# 	except Exception, inst:
# 		# print inst
# 		pass
# 
# 	count = 0
# 	if param.get('choices'):
# 		print "\n\tSuggested values:"
# 		for choice in param.get('choices', []):
# 			print "\t\t%s) %s"%(count, choice)
# 			selections.append(choice)
# 			count += 1
# 
# 	if param.get('vartype') != "choice" and lines:
# 		if param.get('choices'):
# 			print "\n\tOther common values:"
# 		else:
# 			print "\n\tCommon values:"
# 
# 		for line in lines:
# 			print "\t\t%s) %s"%(count, line)
# 			selections.append(line)
# 			count += 1
# 
# 	print "\n\t\t%s) None or N/A"%count
# 	selections.append('')
# 	count += 1
# 
# 	if param.get('vartype') != "choice":
# 		print "\t\t%s) Enter a different not listed above"%count
# 
# 
# 	while True:
# 		inp = raw_input("\n\tSelection (0-%s): "%count)
# 		try:
# 			inp = int(inp)
# 
# 			if inp == count:
# 				inp = raw_input("\tValue: ")
# 			else:
# 				inp = selections[inp]
# 		except:
# 			continue
# 
# 		break
# 
# 	return inp

