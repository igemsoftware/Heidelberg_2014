
# coding: utf-8

# In[1]:

import subprocess
import glob
import numpy as np
from Boinc.setup_project import *
from Boinc import database
import igemathome_database as igemdb
import time

def vectabs(x0, x1, x2):
    return np.sqrt(x0**2 + x1**2 + x2*2)

def return_shortpath(pdbfile, subunit):
	f = open(pdbfile, 'r')
	#print pdbfile


	wholex = []
	wholey = []
	wholez = []
	wholesubunit = []


	#line.split kann nicht verwendet werden, weil manchmal die spalten ineinander verschmelzen, weil das Format doof ist.

	for line in f:
		art = line[:4]
		if art == 'ATOM':
			wholesubunit.append(line[21])

			wholex.append(float(line[31:38]))
			wholey.append(float(line[38:46]))
			wholez.append(float(line[46:54]))

	f.close()

	#aus allen Listen arrays machen
	for thing in [wholex, wholey, wholez, wholesubunit]:
		thing = np.array([thing])

	keep = (wholesubunit == subunit)

	for thing in [wholex, wholey, wholez, wholesubunit]:
		thing = thing[keep]

	shortpath = (vectabs(wholex[0]-wholex[-1], wholey[0] - wholey[-1], wholez[0] - wholez[-1]) < 3 * 7.5)

	return shortpath

# Merken:
#
# In Linkers.txt müssen die ganzen Linker sein, mit allen ausgetauschten Anfangs und Endsequenzen und auch den verschiedenen Winkelmotiven.






exteinlist = ["RGKCWE", "CG"]
startlist = ["GG", ""]


databasefolder = "./import_files/"

database.connect()
#igemdb.connect()

####Hier kann man einfach hinter glob.glob() ein [:10] setzen, um das erstmal auf wengier laufen zu lassen und zu testen


for folder in glob.glob(databasefolder + "*/")[:1]:
	pdbname = folder[-7:-3]
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
