# $Id: __init__.py,v 1.9 2012/02/09 13:22:05 irees Exp $
import glob
from PyQt4 import QtGui, QtCore


def compile():
	from PyQt4 import uic
	for i in glob.glob("*.ui"):
		base = i.replace('.ui', '')
		print "Compiling %s"%base
		fout = open(base+".py", "w")
		uic.compileUi(base+".ui", fout)
		fout.close()


if __name__ == '__main__':
	compile()



import Ui_Login
import Ui_Warning

import Ui_Upload
import Ui_ScanUpload
import Ui_MicroscopeUpload

import Ui_Download

import Ui_Wizard
import Ui_Wizard_Existing
import Ui_Wizard_New
import Ui_Wizard_rectype




__version__ = "$Revision: 1.9 $".split(":")[1][:-1].strip()



