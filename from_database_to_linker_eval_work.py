
# coding: utf-8

# In[1]:

import subprocess
import glob
from Boinc.setup_project import *
from Boinc import database
import igemathome_database as igemdb
import time
import zipfile as zip


boinc_path = "/var/boinc/igemathome"
databasefolder = os.path.join(boinc_path, "import_files")
modeller_results = os.path.join(databasefolder, "finished_circ_modeller")
tmpfolder = os.path.join(boinc_path, "tmp-boinc")
allpdbs = os.path.join(boinc_path, "allpdbs")
database.connect()
#igemdb.connect()

####Hier kann man einfach hinter glob.glob() ein [:10] setzen, um das erstmal auf wengier laufen zu lassen und zu testen


for pdbfolder in glob.glob(modeller_results + os.sep + "*" + os.sep)[:1]:
	pdbname = os.path.basename(os.path.normpath(pdbfolder))
	zipfile = zip.ZipFile(tmpfolder + os.sep + pdbname+".zip", "w")
	if(os.path.isfile(pdbfolder+"/"+pdbname+".pdb")):
		zipfile.write(pdbfolder+"/"+pdbname+".pdb")
	else:
		zipfile.write(allpdbs + os.sep + pdbname + os.sep + pdbname + ".pdb", "master.pdb")
	for resultfile in glob.glob(pdbfolder + "results" + os.sep + "*.pdb"):
		zipfile.write(resultfile, os.path.basename(os.path.normpath(pdbfolder)))

	zipfile.close()

	'''
	pdbfname = pdbname + ".pdb"
	subunit = folder[-2]

	print "folder: %s, pdbname: %s, pdbfname: %s, subunit: %s" % (folder, pdbname, pdbfname, subunit)

	shortpath = return_shortpath(folder + pdbfname, subunit)

	#stage the PDB
	subprocess.call(["bin/stage_file", "--copy", "--gzip", folder + pdbfname])

	proteinjob = igemdb.Job(protein=pdbname, mailaddress="placeholder@igemathome.org")
	proteinjob.commit()
	jobid = proteinjob.id
	wus = dict()

	def setWuByName(wuname, state):
		attempts = 0
		done = False
		print "looking for: '%s'" % wuname
		while attempts < 8 and not done:
			try:
				workunit = database.Workunits.find1(name=wuname)
				wus[workunit.id] = state
				done = True
			except:
				attempts +=1
				time.sleep(0.5)
		if not attempts < 8:
			raise Exception("Mysql", "Unable to get workunit with name: %s" % wuname)

	#create instructions
	for extein in exteinlist:
		for nr in range(1,4):
			if nr == 3:
				if not shortpath:
					for slicing in range(300):
						uniqueforwu = pdbname + "_" + subunit + "_"  + "linker" +"_" + extein + "_" + str(nr) + "_" + str(slicing) +"_"+ str(slicing + 1)

						f = open(folder +"instructions" + "_" + uniqueforwu + ".csv", "w")
						f.write(subunit +"," + uniqueforwu + "," + str(nr) + "," + str(slicing) +","+ str(slicing + 1) + "," + extein + "," "0")
						f.close()
						subprocess.call(["bin/stage_file", "--gzip", folder + "instructions" + "_" + uniqueforwu + ".csv"])
						database.close()
						subprocess.call(["bin/create_work", "--appname", "linker_generator", "--wu_template",
						"templates/linker_gen.input-template", "--result_template", "templates/linker_gen.result-template", "--batch", str(jobid),
						"--wu_name", uniqueforwu , "instructions" + "_" + uniqueforwu + ".csv", pdbfname])
						database.connect()
						setWuByName(uniqueforwu, igemdb.INIT)
				else:
					uniqueforwu = pdbname + "_" + subunit + "_" + "linker" +"_" + extein + "_" + str(nr) + "_" + "shortpath"

					f = open(folder +"instructions" + "_" + uniqueforwu + ".csv", "w")
					f.write(subunit +"," + uniqueforwu + "," + str(nr) + ",0,300" + "," + extein + "," + "1")
					f.close()
					subprocess.call(["bin/stage_file", "--gzip", folder + "instructions" + "_" + uniqueforwu + ".csv"])
					database.close()
					subprocess.call(["bin/create_work", "--appname", "linker_generator", "--wu_template",
					"templates/linker_gen.input-template", "--result_template", "templates/linker_gen.result-template", "--batch", str(jobid),
					"--wu_name", uniqueforwu , "instructions" + "_" + uniqueforwu + ".csv", pdbfname])
					database.connect()
					setWuByName(uniqueforwu, igemdb.INIT)

			else:
				uniqueforwu = pdbname + "_" + subunit + "linker" + "_" + "_" + extein + "_" + str(nr) +"_"+ "0_1"

				f = open(folder +"instructions" + "_" + uniqueforwu + ".csv", "w")
				f.write(subunit +"," + uniqueforwu + "," + str(nr) + ",0,300" + "," + extein + "," + "0")
				f.close()
				subprocess.call(["bin/stage_file", "--gzip", folder + "instructions" + "_" + uniqueforwu + ".csv"])
				database.close()
				subprocess.call(["bin/create_work", "--appname", "linker_generator", "--wu_template",
				"templates/linker_gen.input-template", "--result_template", "templates/linker_gen.result-template", "--batch", str(jobid),
				"--wu_name", uniqueforwu , "instructions" + "_" + uniqueforwu + ".csv", pdbfname])
				database.connect()
				setWuByName(uniqueforwu, igemdb.INIT)

	proteinjob.setWus('linker', wus)
	proteinjob.commit()
	'''
