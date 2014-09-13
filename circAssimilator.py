from assimilator import Assimilator
from Boinc.tools import *
from Boinc.boinc_db import *
import shutil
import os


class linkerAssimilator(Assimilator):
	def __init__(self):
		Assimilator.__init__(self)
		self.appname = 'circ_modeller'
		self.update_db = False
		self.basedir = "./results"
		if not os.path.isdir(self.basedir):
			os.mkdir(self.basedir)
		self.basedir = self.basedir + "/" + self.appname

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

		valid_count = 0

		for result in results:
			if result.validate_state == VALIDATE_STATE_VALID:
				print "valid result:"
				filename = "%s_0" % result.name
				savepath = resultpath
				resultfile = get_output_file_path(filename)
				print "   Filename: %s" % filename
				print "   Filepath: %s" % resultfile
				try:
					shutil.copy2(resultfile, resultpath+"/"+os.path.basename(resultfile)[:-2]+".pdb")
				except:
					print "   Resultfile missing... only saving stderr"
					savepath = pdbfolder + "/missing"
					if not os.path.isdir(savepath):
						os.mkdir(savepath)

				f = open(savepath+"/"+os.path.basename(resultfile)[:-2]+"_stderr.txt", 'w')
				f.write(result.stderr_out)
				f.close()
				valid_count += 1
				print
			else:
				errorpath = pdbfolder+"/errors"
				if not os.path.isdir(errorpath):
					os.mkdir(errorpath)
				print "invalid result"
				f = open(errorpath+"/"+result.name+"_stderr.txt", 'w')
				f.write(result.stderr_out)
				f.close()
				print

		if(valid_count == 0):
			f = open(pdbfolder+"/resubmit", 'w')
			f.write(wu.name+"\n")
			f.close()



if __name__ == '__main__':
    asm = linkerAssimilator()
    asm.run()