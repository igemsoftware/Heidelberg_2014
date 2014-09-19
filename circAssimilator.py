from assimilator import Assimilator
from Boinc.tools import *
from Boinc.boinc_db import *
import shutil
import os
import xml.etree.ElementTree as ET
from subprocess import check_output

class circModeller_Assimilator(Assimilator):
	def __init__(self):
		Assimilator.__init__(self)
		self.appname = 'circ_modeller'
		self.basedir = "./database"
		if not os.path.isdir(self.basedir):
			os.mkdir(self.basedir)
		self.basedir += "/finished_"
		self.basedir = self.basedir + self.appname

		if not os.path.isdir(self.basedir):
			os.mkdir(self.basedir)

		self.save_pdbs = True

	def save_inputfiles(self, wu, path, files): # Gets a tuble with input filenames (unresolved) to save from workunit
		root = ET.fromstring("<root>" + wu.xml_doc + "</root>")
		for file in root.findall("./workunit/file_ref"):
			boincname = file.find("open_name").text
			if boincname in files:
				resname = file.find("file_name").text
				# Get filepath via dir_hier_path and remove tailing spaces and newlines
				filepath = check_output(['bin/dir_hier_path', resname])
				filepath = filepath.strip('\n ')
				
				if os.path.isfile(filepath):
					self.logDebug("Copying %s to %s\n" % (filepath, path))
					shutil.copy(filepath, path)
				else:
					self.logCritical("Unable to copy %s: %s, file does not exist.\n" % (boincname, filepath))
			
			elif boincname == "atomfile.pdb" and self.save_pdbs:
				resname = file.find("file_name").text
				pdbfname = wu.name[:4]+ ".pdb"
				if not os.path.exists(path+"/"+pdbfname):
					filepath = check_output(['bin/dir_hier_path', resname])
					filepath = filepath.strip('\n ')
					if os.path.isfile(filepath):
						self.logDebug("Saving pdb %s\n" % filepath)
						if not os.path.exists(path + "/" wu.name[:4]):
							shutil.copy(filepath, path+"/" + pdbfname)
						else:
							self.logDebug("Pdbfile %s already exists!\n" % path+ "/" + pdbfname)
					else:
						self.logCritical("Unable to save pdb %s, file does not exist.\n")


	def assimilate_handler(self, wu, results, canonical_result):
		pdbfolder = self.basedir + "/" + wu.name[:6]
		if not os.path.isdir(pdbfolder):
			os.mkdir(pdbfolder)

		resultpath = pdbfolder+"/results"
		if not os.path.isdir(resultpath):
			os.mkdir(resultpath)

		self.save_inputfiles(wu, resultpath, ["configfile.csv","inputsequencefile.ali"])
		
		valid_count = 0
		
		for result in results:
			if result.validate_state == VALIDATE_STATE_VALID:
				'''
				We only get one resultfile, which is normally named resultname_0, as it is the first file.
				Save result pdb as resultname.pdb and stderr as resultname_stderr.txt in the pdbfolder.
				'''
				filename = "%s_0" % result.name
				savepath = resultpath
				resultfile = get_output_file_path(filename)
				targetfile = os.path.split(resultfile)[1] #remove path
				targetfile = "_".join(targetfile.split("_")[:-1])+".pdb" #removes terminal _0
				try:
					shutil.copy(resultfile, resultpath+"/"+targetfile)
				except:
					self.logCritical("Resultfile of #%s: %s missing... only saving stderr\n" % (str(result.id), result.name) )
					savepath = pdbfolder + "/missing"
					if not os.path.isdir(savepath):
						os.mkdir(savepath)

				f = open(savepath+"/"+os.path.basename(targetfile)+"_stderr.txt", 'w')
				f.write(result.stderr_out)
				f.close()
				valid_count += 1
			else:
				'''
				Save the stderr of failed results into the subdir errors in the pdbfolder
				'''
				errorpath = pdbfolder+"/errors"
				if not os.path.isdir(errorpath):
					os.mkdir(errorpath)
				self.logNormal("Result #%s: %s contains errors, saving stderr\n" % (str(result.id), result.name) )
				f = open(errorpath+"/"+result.name+"_stderr.txt", 'w')
				f.write(result.stderr_out)
				f.close()

		if(valid_count == 0):
			self.logCritical("Workunit #%s: %s has no valid result, adding to resubmit file\n" % (str(result.id), result.name) )
			f = open(pdbfolder+"/resubmit", 'w')
			f.write(wu.name+"\n")
			f.close()

		self.report_errors(wu)


if __name__ == '__main__':
    asm = circModeller_Assimilator()
    asm.run()
