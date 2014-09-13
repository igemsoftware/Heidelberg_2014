
# coding: utf-8

# In[1]:

import subprocess
import glob
import numpy as np


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
startlist = ["GG"]


databasefolder = "./import_files/"



####Hier kann man einfach hinter glob.glob() ein [:10] setzen, um das erstmal auf wengier laufen zu lassen und zu testen

for folder in glob.glob(databasefolder + "*/")[:1]:
    pdbname = folder[offset:offset + 4]
    pdbfname = pdbname + ".pdb"
    subunit = folder[offset + 5]
    
    shortpath = return_shortpath(pdbfname, subunit)
    
    #stage the PDB
    subprocess.call(["bin/stage_file", "--copy", "--gzip", folder + pdbfname])
    
    #create instructions
    for extein in exteinlist:
		for nr in range(1,4):
			if nr == 3:
				if not shorpath:
					for slicing in range(300):
						uniqueforwu = pdbname + "_" + subunit + "_"  + "linker" +"_" + extein + str(nr) + "_" + str(slicing) +"_"+ str(slicing + 1)
			
						f = open(folder +"instructions" + "_" + uniqueforwu + ".csv", "w")
						f.write(subunit +"," + uniqueforwu + "," + "1" + "," + str(slicing) +","+ str(slicing + 1) + "," + extein, "0")
						f.close()
						subprocess.call(["bin/stage_file", "--gzip", folder + "instructions" + "_" + uniqueforwu + ".csv"])
						subprocess.call(["bin/create_work", "--appname", "linker_generator", "--wu_template", 
					 "templates/circ_modeller.input-template", "--result_template", "templates/circ_modeller.result-template",
					 "--wu_name", uniqueforwu , "instructions" + "_" + uniqueforwu + ".csv", pdbfname])
				else:
					uniqueforwu = pdbname + "_" + subunit + "_" + "linker" +"_" + extein + str(nr) + "_" + "shortpath"
			
						f = open(folder +"instructions" + "_" + uniqueforwu + ".csv", "w")
						f.write(subunit +"," + uniqueforwu + "," + "1" + ",0,300" + "," + extein, "1")
						f.close()
						subprocess.call(["bin/stage_file", "--gzip", folder + "instructions" + "_" + uniqueforwu + ".csv"])
						subprocess.call(["bin/create_work", "--appname", "linker_generator", "--wu_template", 
					 "templates/circ_modeller.input-template", "--result_template", "templates/circ_modeller.result-template",
					 "--wu_name", uniqueforwu , "instructions" + "_" + uniqueforwu + ".csv", pdbfname])
					
			else:
				uniqueforwu = pdbname + "_" + subunit + "linker" + "_" + "_" + extein + str(nr) +"_"+ "0_1"
		
					f = open(folder +"instructions" + "_" + uniqueforwu + ".csv", "w")
					f.write(subunit +"," + uniqueforwu + "," + str(nr) + ",0,300" + "," + extein, "0")
					f.close()
					subprocess.call(["bin/stage_file", "--gzip", folder + "instructions" + "_" + uniqueforwu + ".csv"])
					subprocess.call(["bin/create_work", "--appname", "linker_generator", "--wu_template", 
				 "templates/circ_modeller.input-template", "--result_template", "templates/circ_modeller.result-template",
				 "--wu_name", uniqueforwu , "instructions" + "_" + uniqueforwu + ".csv", pdbfname])

