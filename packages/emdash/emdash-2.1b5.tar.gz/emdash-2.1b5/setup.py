import os
import subprocess

from distutils.core import setup

from emdash import VERSION
URLBASE = "http://ncmi.bcm.edu/ncmi/software/EMEN2"
URLMAP = {
	"daily": "software_94",
	"2.0rc1": "software_105",
	"2.0rc2": "software_107",
	"2.0rc3": "software_108",
	"2.0rc4": "software_110",	
	"2.0rc5": "software_113",
	"2.0rc6": "software_114",
	"2.0rc7": "software_117"
}

if __name__ == "__main__":
	setup(
		name='emdash',
		version=VERSION,
		description='EMDash -- Client utilities for EMEN2',
		author='Ian Rees',
		author_email='ian.rees@bcm.edu',
		url='http://blake.grid.bcm.edu/emanwiki/EMEN2/',
		download_url="%s/%s/emdash-%s.tar.gz"%(URLBASE, URLMAP.get(VERSION,'daily'), VERSION),
		packages=[
			'emdash',
			'emdash.ui'
			],
		scripts=['scripts/emen2client.py']
		)
