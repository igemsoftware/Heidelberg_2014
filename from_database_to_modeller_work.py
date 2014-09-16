
# coding: utf-8

# In[1]:

import subprocess
import glob
import os
import numpy as np

# Merken:
# 
# In Linkers.txt müssen die ganzen Linker sein, mit allen ausgetauschten Anfangs und Endsequenzen und auch den verschiedenen Winkelmotiven.

# In[2]:

rods = ["AEAAAK", "AEAAAKA", "AEAAAKAA", "AEAAAKEAAAK", "AEAAAKEAAAKA", "AEAAAKEAAAKEAAAKA", "AEAAAKEAAAKEAAAKEAAAKA",
        "AEAAAKEAAAKEAAAKEAAAKEAAAKA"]
angles =["AASGAA", "AALAA", "AAWAA", "ASNA", "ASA", "AGA", "VV"]


# In[3]:

#create all the different linkers until maximum 1 edge from the above pieces
LINKERS = []
temp = []
for angle in angles:
    for rod in rods:
        temp.append("AEAAAK" + angle + rod)
        
LINKERS += temp
LINKERS += rods


# In[4]:

#attach extein and starting sequence:

exteinlist = ["RGKCWE"]
startlist = ["GG"]

templist = []
for linker in LINKERS:
    for start in startlist:
        temp = start + linker
        for extein in exteinlist:
            templist.append(temp + extein)
LINKERS = templist
templist = None


# In[5]:
def create_helicalrangelist(linkerlist):
    '''
    returns a list of the helical ranges of the linker.
    Always a list of twolists, with start and end of helix
    '''
    
    #create helicalrangelist
    helicalrange = []
    for linker in linkerlist:
        seq = []
        helixcount = 0
        for i in range(len(linker)):
            if ((linker[i] == "A") | (linker[i] == "E") | (linker[i] == "K")):
                helixcount += 1
            else:
                helixcount = 0
            if (i < (len(linker) -2)):
                if ((helixcount > 5) & (linker[i +1] != "A") & (linker[i + 1] != "E") & (linker[i + 1] != "K")):
                    seq = seq + [i - helixcount + 3, i]
                    helixcount = 0
            elif ((helixcount > 5) & (i == (len(linker) -2))):
                seq = seq + [i - helixcount + 3, i + 1]
                helixcount = 0
            elif ((helixcount > 5) & (i == (len(linker) -1))):
                seq = seq + [i - helixcount + 3, i]
                helixcount = 0
                
        helicalrange.append(seq)
    return helicalrange
    
    
exchangedict = {"RGKCWE":["RGKCWE"]}


# In[19]:

print LINKERS
print helicalrange
databasefolder = "./import_files/"
offset = len(databasefolder)

####Hier kann man einfach hinter glob.glob() ein [:10] setzen, um das erstmal auf wengier laufen zu lassen und zu testen

for folder in glob.glob(databasefolder + "*/")[:1]:
    pdbname = folder[offset:offset + 4]
    pdbfname = pdbname + ".pdb"
    subunit = folder[offset + 5]
    
    sequencesfromlinker = []
    lengtoflinker = []
    if os.path.exists(folder + "resultsfromlinkers/"):
        for resultfile in glob.glob(folder + "resultsfromlinkers/*"):
            header = True
            for line in resultsfile:
                if header:
                    header = False
                else:
                    line = line.strip()
                    cols = line.split()
                    sequencesfromlinker.append(cols[0])
                    lengthoflinker.append(cols[10])
        sequencesfromlinker = np.array(sequencesfromlinker)
        lengthoflinker = np.array(lengthoflinker)
        
        sequencepool = np.unique(sequencesfromlinker)
        sequenceweightings = []
        for sequenceiter in sequencepool:
            sequenceweightings.append(np.mean(weightingsall[0][sequences == sequenceiter]))
            
        sequenceweightings = np.array(sequenceweightings)
        
        sortarray = np.argsort(sequenceweightings)
        sequencepool = sequencepool[sortarray]
        
        if np.size(sequencepool) > 100:
            sequencepool = sequencepool[100]
        allsequences = []
        #das verändern der Sequenzen:
        for sequence in sequencepool:
            for i in range(1,4):
                for key in exchangedict:
                    for otherstring in exchangedict[key]:
                        allsequences.append(replace(sequence, key, otherstring, i)
        f = open(folder + "linkers.txt", "w")
        for linker in allsequences:
            if linker == allsequences[0]:
                writestring = linker
            else:
                writestring += ("," + linker)
        f.write(writestring + "\n")
        
        helicalrange = create_helicalrangelist(allsequences)
        writestring = ""
        for linkerrange in helicalrange:
            for bond in linkerrange:
                writestring += (str(bond) + " ")
            writestring += ","
        writestring = writestring[:-1] + "\n"
        f.write(writestring)
        f.close()
        
    
    
    if not os.path.exists(folder + "linkers.txt"):
        
        helicalrange = create_helicalrangelist(LINKERS)
        
        f = open(folder + "linkers.txt", "w")
        for linker in LINKERS:
            if linker == LINKERS[0]:
                writestring = linker
            else:
                writestring += ("," + linker)
        f.write(writestring + "\n")
        writestring = ""
        for linkerrange in helicalrange:
            for bond in linkerrange:
                writestring += (str(bond) + " ")
            writestring += ","
        writestring = writestring[:-1] + "\n"
        f.write(writestring)
        f.close()
        
    #stage the PDB
    subprocess.call(["bin/stage_file", "--gzip", folder + pdbfname])
    #create .ali files
    f = open(folder + pdbname + "_" + subunit + ".seq", "r")
    sequence = f.readline()
    sequence = sequence.strip()
    f.close()
    
    f = open(folder + "linkers.txt", "r")
    linkers = f.readline()
    linkers = linkers.strip()
    linkerlist = linkers.split(",")
    temp = []
    helixes = f.readline()
    helixes = helixes.strip()
    helixranges = helixes.split(",")
    for onelinker in helixranges:
        onelinker = onelinker.strip()
        onelinker = onelinker.split()
        temp.append(onelinker)
    helixranges = temp
    temp = None
    f.close()



    seqlength = len(sequence)
    for i in range(len(linkerlist)):
        uniqueforwu = pdbname + "_" + subunit + "_modeller_ " + "linker_" + str(i)
        alifname = uniqueforwu + ".ali"
        f = open(folder + alifname, "w")
        f.write(">P1;" + uniqueforwu + "\n")
        f.write("sequence:" + uniqueforwu + ":::::::0.00: 0.00\n")
        f.write(sequence + linkerlist[i] + "*\n")
        f.close()
        
        linkerend = len(linkerlist[i]) + seqlength
        
        #configfile
        configfname = "configfile_" + uniqueforwu + ".csv"
        f = open(folder + configfname, "w")
        #TODO: darüber sprechen, was da reinsoll
        helixrangestring = ""
        for startend in helixranges[i]:
            #creates with comma for inserting it into file WATCHOUT!!!!!!!!!!
            helixrangestring += ("," + str(int(startend) + seqlength))
        f.write(pdbname + "," + uniqueforwu + "," + subunit + "," + seqlength "," + linkerend + helixrangestring)
        f.close()
        
        #make the signature of all files
        subprocess.call(["bin/file_signer", "../private_key.pem", folder + "signatures_" + uniqueforwu,
                         "configfile.csv", folder + configfname, "atomfile.pdb", folder + pdbfname,
                         "inputsequencefile.ali", folder + alifname])
        
        #stage the new files first .ali and then configfile
        subprocess.call(["bin/stage_file", "--gzip", folder + configfname])
        subprocess.call(["bin/stage_file", "--gzip", folder + alifname])
        subprocess.call(["bin/stage_file", "--gzip", folder + "signatures_" + uniqueforwu])
        #create work
        subprocess.call(["bin/create_work", "--appname", "circ_modeller", "--wu_template", 
                         "templates/circ_modeller.input-template", "--result_template", "templates/circ_modeller.result-template",
                         "--wu_name", uniqueforwu , configfname, pdbfname, alifname,
                         "signatures_" + uniqueforwu])

