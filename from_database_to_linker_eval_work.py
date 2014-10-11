import subprocess
import glob
from Boinc.setup_project import *
from Boinc import database
import igemathome_database as igemdb
import time
import zipfile as zip
import md5



boinc_path = "/var/boinc/igemathome"
databasefolder = os.path.join(boinc_path, "database")
modeller_results = os.path.join(databasefolder, "finished_circ_modeller")
staged_for_linker_eval = os.path.join(databasefolder, "staged_for_linker_evaluator")
tmpfolder = os.path.join(boinc_path, "tmp_boinc")
allpdbs = os.path.join(boinc_path, "allpdbs")
database.connect()
#igemdb.connect()

####Hier kann man einfach hinter glob.glob() ein [:10] setzen, um das erstmal auf wengier laufen zu lassen und zu testen


for pdbfolder in glob.glob(modeller_results + os.sep + "*" + os.sep)[:10]:
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

	pdbname = os.path.basename(os.path.normpath(pdbfolder))
	zipfile_path = tmpfolder + os.sep + pdbname + ".zip"
	zipfile = zip.ZipFile(zipfile_path, "w")

	m = md5.new()

	if(os.path.isfile(pdbfolder+"/"+pdbname+".pdb")):
		zipfile.write(pdbfolder+"/"+pdbname+".pdb")
	else:
		zipfile.write(allpdbs + os.sep + pdbname + os.sep + pdbname.split('_')[0] + ".pdb", "master.pdb")

	m.update("master.pdb")

	for resultfile in glob.glob(pdbfolder + "results" + os.sep + "*_0.pdb"):
		zipfile.write(resultfile, os.path.basename(os.path.normpath(resultfile)))
		m.update(os.path.basename(os.path.normpath(resultfile)))

	zipfile.close()

	md5hash = m.hexdigest()

	zipfile_path_new = os.path.splitext(zipfile_path)[0] + "_" + md5hash[:5] + os.path.splitext(zipfile_path)[1]

	shutil.move(zipfile_path, zipfile_path_new)

	zipfile_path = zipfile_path_new

	proteinjob = igemdb.Job(protein=pdbname, mailaddress="placeholder@igemathome.org")
	proteinjob.commit()
	jobid = proteinjob.id
	try:
		wus = proteinjob.getWus("evaluator")
	except:
		wus = dict()

	subprocess.call(["bin/stage_file", zipfile_path])

	database.close()
	subprocess.call(["bin/create_work", "--appname", "linker_evaluator", "--wu_template",
						"templates/linker_evaluator.input-template", "--result_template", "templates/linker_evaluator.result-template", "--batch", str(jobid),
						"--wu_name", os.path.splitext(os.path.basename(zipfile_path))[0], os.path.basename(zipfile_path)])

	if not os.path.isdir(staged_for_linker_eval):
		os.mkdir(staged_for_linker_eval)

	shutil.move(pdbfolder, staged_for_linker_eval)

	database.connect()

	setWuByName(os.path.splitext(os.path.basename(zipfile_path))[0], igemdb.INIT)

	proteinjob.commit()

