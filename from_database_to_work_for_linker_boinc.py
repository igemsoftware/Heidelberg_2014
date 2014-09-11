
# coding: utf-8

# In[1]:

import subprocess
import glob


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
    
    #stage the PDB
    subprocess.call(["bin/stage_file", "--gzip", folder + pdbfname])
    
    #create instructions
    for extein in exteinlist:
		for nr in range(1,4):
			if nr == 3:
				for slicing in range(100):
					uniqueforwu = pdbname + "_" + subunit + "_" + extein + str(nr) + "_" + str(slicing) +"_"+ str(slicing + 1)
		
					f = open(folder +"instructions" + "_" + uniqueforwu + ".csv", "w")
					f.write(subunit +"," + uniqueforwu + "," + "1" + "," + str(slicing) +","+ str(slicing + 1) + "," + extein)
					f.close()
					subprocess.call(["bin/stage_file", "--gzip", folder + "instructions" + "_" + uniqueforwu + ".csv"])
					subprocess.call(["bin/create_work", "--appname", "linker_generator", "--wu_template", 
				 "templates/circ_modeller.input-template", "--result_template", "templates/circ_modeller.result-template",
				 "--wu_name", uniqueforwu , "instructions" + "_" + uniqueforwu + ".csv", pdbfname])
					
			else:
				uniqueforwu = pdbname + "_" + subunit + "_" + extein + str(nr) +"_"+ str(slicing + 1)
		
					f = open(folder +"instructions" + "_" + uniqueforwu + ".csv", "w")
					f.write(subunit +"," + uniqueforwu + "," + "1" + "," + 0 +","+ 100 + "," + extein)
					f.close()
					subprocess.call(["bin/stage_file", "--gzip", folder + "instructions" + "_" + uniqueforwu + ".csv"])
					subprocess.call(["bin/create_work", "--appname", "linker_generator", "--wu_template", 
				 "templates/circ_modeller.input-template", "--result_template", "templates/circ_modeller.result-template",
				 "--wu_name", uniqueforwu , "instructions" + "_" + uniqueforwu + ".csv", pdbfname])

