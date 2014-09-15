from assimilator import Assimilator
from Boinc.tools import *
from Boinc.boinc_db import *
from Boinc import database
import shutil
import os
import xml.etree.ElementTree as ET
from subprocess import check_output
import igemathome_database as igemdb



class circModeller_Assimilator(Assimilator):
	def __init__(self):
		Assimilator.__init__(self)
		self.appname = 'linker_generator'
		self.databasedir = "./temp-database"
		if not os.path.isdir(self.databasedir):
			os.mkdir(self.databasedir)
		self.basedir = self.databasedir + "/finished_"
		self.basedir = self.basedir + self.appname

		if not os.path.isdir(self.basedir):
			os.mkdir(self.basedir)

		self.save_pdbs = False
		self.update_db = False
		igemdb.connect()

	def checkBatchComplete(self, wu):
		batchid = wu.batch
		database.connect()
		wus = database.Workunits.count(batch=batchid)
		finished_wus = database.Workunits.count(batch=batchid, assimilate_state=ASSIMILATE_DONE )
		print "There are still %i unassimilated Workunits for Batch %i" % (wus-finished_wus, batchid)


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
				if not os.path.exists(path+"/"+resname):
					filepath = check_output(['bin/dir_hier_path', resname])
					filepath = filepath.strip('\n ')
					if os.path.isfile(filepath):
						self.logDebug("Saving pdb %s\n" % filepath)
						shutil.copy(filepath, path)
					else:
						self.logCritical("Unable to save pdb %s, file does not exist.\n")


	def assimilate_handler(self, wu, results, canonical_result):
		pdbfolder = self.basedir + "/" + wu.name[:6]
		if not os.path.isdir(pdbfolder):
			os.mkdir(pdbfolder)

		resultpath = pdbfolder+"/results"
		if not os.path.isdir(resultpath):
			os.mkdir(resultpath)

		self.save_inputfiles(wu, resultpath, ["instructions.txt"])
		
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
				targetfile = "_".join(targetfile.split("_")[:-1]) #removes terminal _0
				try:
					shutil.copy(resultfile, resultpath+"/"+targetfile)
					valid_count += 1
				except:
					self.logCritical("Resultfile of #%s: %s missing... only saving stderr\n" % (str(result.id), result.name) )
					savepath = pdbfolder + "/missing"
					if not os.path.isdir(savepath):
						os.mkdir(savepath)

				f = open(savepath+"/"+os.path.basename(targetfile)+"_stderr.txt", 'w')
				f.write(result.stderr_out)
				f.close()
				
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

		Job = igemdb.Jobs.find1(id=wu.batch)
		wus = Job.getWus('linker')

		if valid_count == 0:
			self.logCritical("Workunit #%s: %s has no valid result, adding to resubmit file\n" % (str(result.id), result.name) )
			f = open(pdbfolder+"/resubmit", 'w')
			f.write(wu.name+"\n")
			f.close()
			Job = igemdb.Jobs.find1(id=wu.batch)
			errorwus = Job.getErrorWus()
			errorwus += wu.id
               Job.setErrorWus(errorwus)
               Job.commit()
		else:
			wus[wu.id] = igemdb.FINISHED
			Job.setWus('linker', wus)
			Job.commit()

		#Check for missing Workunits, cannot continue to modeller if not all files are ready

		missing = []
		for wuid, state in wus.iteritems():
			if(state == igemdb.INIT):
				missing += wuid

		if len(missing) == 0:
			print "Workunit #%i: %s is ready for modelling" % (wu.id, wu.name)
               modeller_staged = self.databasedir + "/staged_modeller"
               if not os.path.isdir(modeller_staged):
                         os.mkdir(modeller_staged)
               
               shutil.move(pdbfolder, modeller_staged)

               Job.linker_state = igemdb.FINISHED
               Job.commit()

			# Do something, like staging the files and creating work for modeller
		else:
               self.logDebug("Job #%i is missing %i Workunits\n" % (Job.id, len(missing)))
               for wuid in missing:
                    missingresults = database.Workunits.find(workunitid=wuid, )
                    .report_deadline
               self.logDebug("Estimated finish time: \n")

		# TODO resubmit Wu if failed

		self.report_errors(wu)


if __name__ == '__main__':
    asm = circModeller_Assimilator()
    asm.run()