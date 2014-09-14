from assimilator import Assimilator
from Boinc.tools import *
from Boinc.boinc_db import *
from parse import compile
import shutil
import os


class linkerAssimilator(Assimilator):
	def __init__(self):
		Assimilator.__init__(self)
		self.appname = 'linker_gen'
		self.update_db = False
		self.basedir = "./results"
		if not os.path.isdir(self.basedir):
			os.mkdir(self.basedir)


	def assimilate_handler(self, wu, results, canonical_result):
		print "Resultfiles for %s: " % wu.name
		pdbfolder = self.basedir + "/" + wu.name[:6]
		if not os.path.isdir(pdbfolder):
			os.mkdir(pdbfolder)

		resultpath = pdbfolder+"/results"
		if not os.path.isdir(resultpath):
			os.mkdir(resultpath)

		for result in results:
			if result.validate_state == VALIDATE_STATE_VALID:
				print "valid result:"
				filename = "%s_0" % result.name
				resultfile = get_output_file_path(filename)
				print "   Filename: %s" % filename
				print "   Filepath: %s" % resultfile
				shutil.copy2(resultfile, resultpath+"/"+os.path.basename(resultfile))
				f = open(resultpath+"/"+os.path.basename(resultfile)+"_stderr.txt", 'w')
				f.write(result.stderr_out)
				f.close()
			else:
				errorpath = resultpath+"/errors"
				if not os.path.isdir(errorpath):
					os.mkdir(errorpath)
				print "invalid result"
				f = open(errorpath+"/"+result.name+"_stderr.txt", 'w')
				f.write(result.stderr_out)
				f.close()


if __name__ == '__main__':
    asm = linkerAssimilator()
    asm.run()