
# coding: utf-8

# In[1]:

# einlesen des PDB files. die Dateien sollten in proteine gespeichert werden
import numpy as np
import loader

# Betrag eines Vektors
def vectabs(x0, x1, x2):
    return np.sqrt(x0**2 + x1**2 + x2*2)


def vectabsar(ar):
    return np.sqrt(ar[:, 0]**2+ar[:, 1]**2+ar[:, 2]**2)


def ebene(a, b, c):
    '''
    gibt normalenvektor zu ebene von drei Punkten aus, bereits normiert
    '''
    x0 = (a-b)[1]*(c-b)[2]-((a-b)[2]*(c-b)[1])
    x1 = (a-b)[2]*(c-b)[0]-((a-b)[0]*(c-b)[2])
    x2 = (a-b)[0]*(c-b)[1]-((a-b)[1]*(c-b)[0])

    xabs = vectabs(x0, x1, x2)

    return np.array([x0/xabs, x1/xabs, x2/xabs])


# einen Vektor mit Drehmatrix drehen um a-achse
def drehenx(phi, x, y, z):
    x1 = x * np.cos(phi * 0)
    y1 = y * np.cos(phi) - z * np.sin(phi)
    z1 = y * np.sin(phi) + z * np.cos(phi)
    return np.array([x1, y1, z1])


def dreheny(phi, x, y, z):
    x1 = x * np.cos(phi) - z * np.sin(phi)
    y1 = y * np.cos(phi * 0)
    z1 = x * np.sin(phi) + z * np.cos(phi)
    return np.array([x1, y1, z1])


def drehenz(phi, x, y, z):
    x1 = x * np.cos(phi) - y * np.sin(phi)
    y1 = x * np.sin(phi) + y * np.cos(phi)
    z1 = z * np.cos(phi * 0)
    return np.array([x1, y1, z1])


def drehenxy(phi, theta, v):
    '''
    dreht Vektor v (als np.array) um phi um die x-Achse, und theta um die
    y-Achse
    '''
    v = drehenx(phi, v[0], v[1], v[2])
    return dreheny(theta, v[0], v[1], v[2])


def abstand(x, y):
    '''
    den Abstand zweier Punkte bestimmen, den Punkt als Array eingeben.
    '''
    return np.sqrt((x[0]-y[0])**2+(x[1]-y[1])**2+(x[2]-y[2])**2)


def betrag(x):
    return np.sqrt((x[0])**2+(x[1])**2+(x[2])**2)


def abstandpktzuarray(x, ar):
    return np.sqrt((x[0]-ar[:, 0])**2+(x[1]-ar[:, 1])**2+(x[2]-ar[:, 2])**2)


def abstandarrays(ar1, ar2):
    return np.sqrt((ar1[:, 0] - ar2[:, 0])**2 +
                   (ar1[:, 1] - ar2[:, 1])**2 + (ar1[:, 2] - ar2[:, 2])**2)


def abstandarrays_quadr(ar1, ar2):
    return (ar1[:, 0]-ar2[:, 0])**2+(ar1[:, 1] - ar2[:, 1])**2 +\
           (ar1[:, 2] - ar2[:, 2])**2


def skalar_product(ar1, ar2):
    return (ar1[:, 0]*ar2[:, 0])+(ar1[:, 1]*ar2[:, 1])+(ar1[:, 2]*ar2[:, 2])


def angle_between_connections_array(startingarray, middlearray, endingarray):

    '''
    calculates the angles between the vectors from startingarray to
    middlearray and middlearray to endingarray.
    If there is no displacement between the arrays it returns zero as angle.
    startingarray and endingarray can be only one single point,
    middlearray should always be an array of points in 3d space.

    returns values between [0,pi] in an array of size Startarray.
    '''

    if np.shape(startingarray) == (3,):
        startingexp = np.repeat([startingarray],
                                np.size(middlearray, axis=0), axis=0)
    else:
        startingexp = startingarray
    if np.shape(endingarray) == (3,):
        endingexp = np.repeat([endingarray],
                              np.size(middlearray, axis=0), axis=0)
    else:
        endingexp = endingarray

    vect1 = (startingexp - middlearray)
    vect2 = (endingexp - middlearray)
    return angle_between_vectors(vect1, vect2)


def angle_between_vectors(vect1, vect2):
    '''
    calculates the angle between two arrays of vectors. If one of the vectors
    is 0, the angle is set to 0. The result is based on arccos.

    returns the angles between two vectors.

    '''
    lengthofarrays = np.size(vect1, axis=0)
    # catch if there is 0 displacement
    tocalculate = (((vect1 != np.array([0, 0, 0])).any(1)) &
                   ((vect2 != np.array([0, 0, 0])).any(1)))
    if tocalculate.any():
        vect1 = vect1[tocalculate]
        vect2 = vect2[tocalculate]
        catchrounding = skalar_product(vect1, vect2)/(vectabsar(vect1) *
                                                      vectabsar(vect2))
        # get rounding arrors
        catchrounding[catchrounding > 1] = 1
        catchrounding[catchrounding < -1] = -1
        angles = np.arccos(catchrounding)
        returnangles = np.zeros(lengthofarrays)
        returnangles[tocalculate] = angles
    else:
        returnangles = np.zeros(lengthofarrays)
    return returnangles


# In[3]:


def distance_from_connection(Startarray, Endarray, Points):
    '''
takes a connection from Startarray to Endarray and calculates the perpendicular
distance of the points from the connection. Startarray or Endarray
can also be single points.

Returns an array of size (start * points) with all perpendicular distances
or distances of the endpoints.

    '''
    if np.shape(Startarray) == (3,):
        if np.shape(Endarray) != (3, ):
            Starttemp = np.repeat([Startarray], np.size(Endarray, axis=0),
                                  axis=0)
        else:
            Starttemp = np.reshape(Startarray, (1, 3))
    else:
        Starttemp = Startarray

    if np.shape(Endarray) == (3, ):
        if np.shape(Startarray) != (3, ):
            Endtemp = np.repeat([Endarray], np.size(Startarray, axis=0),
                                axis=0)
        else:
            Endtemp = np.reshape(Endarray, (1, 3))
    else:
        Endtemp = Endarray


    # reshape the arrays and the points, have a Points*Start array
    oneaxis = np.size(Starttemp, axis=0)
    twoaxis = np.size(Points, axis=0)

    Starttemp = np.repeat(Starttemp, twoaxis, axis=0)
    Endtemp = np.repeat(Endtemp, twoaxis, axis=0)
    Points = np.tile(Points, (oneaxis, 1))

    StartPunkteAbst = abstandarrays(Starttemp, Points)
    StartPunkteAbst = np.reshape(StartPunkteAbst, (oneaxis, twoaxis))

    EndPunkteAbst = abstandarrays(Endtemp, Points)
    EndPunkteAbst = np.reshape(EndPunkteAbst, (oneaxis, twoaxis))

    AngleAtStart = angle_between_connections_array(Points, Starttemp, Endtemp)
    AngleAtStart = np.reshape(AngleAtStart, (oneaxis, twoaxis))

    AngleAtEnd = angle_between_connections_array(Points, Endtemp, Starttemp)
    AngleAtEnd = np.reshape(AngleAtEnd, (oneaxis, twoaxis))



    # die Punkte mit über 90° nehmen einfach den Abstand vom Ende,
    # die kleiner als 90° den senkrechten Abstand
    StartBiggerNinetyBool = (AngleAtStart > np.pi/2)
    EndBiggerNinetyBool = (AngleAtEnd > np.pi/2)
    pointonconnectionbool = (AngleAtStart == 0) & (AngleAtEnd == 0)
    NotUseBool = np.invert(StartBiggerNinetyBool | EndBiggerNinetyBool |
                           pointonconnectionbool)
    DistanceFromConnection = np.empty((oneaxis, twoaxis))
    DistanceFromConnection[NotUseBool] = (np.sin(AngleAtStart[NotUseBool]) *
                                          StartPunkteAbst[NotUseBool])
    DistanceFromConnection[EndBiggerNinetyBool] = EndPunkteAbst[EndBiggerNinetyBool]
    DistanceFromConnection[StartBiggerNinetyBool] = StartPunkteAbst[StartBiggerNinetyBool]
    DistanceFromConnection[pointonconnectionbool] = 0.
    return DistanceFromConnection, oneaxis, twoaxis


# In[4]:

'''

def reduce_proteinpoints(proteinpoints, minabstand):
    for i in range(len(np.size(proteinpoints, axis=0))):
        if i == 0:
            checkpoints = proteinpoints
        point = proteinpoints[i]
        #slice all points in the area of a cube with axeslength minabstand. If there is another
        #proteinpoint a linker would already be sorted out by the other point.
        usebool = ((checkpoints[:,0] > (point[0] - minabstand)) & (checkpoints[:,0] < (point[0] + minabstand)) &
                   (checkpoints[:,1] > (point[1] - minabstand)) & (checkpoints[:,1] < (point[1] + minabstand)) &
                   (checkpoints[:,2] > (point[2] - minabstand)) & (checkpoints[:,2] < (point[2] + minabstand)))
        hereusepoints = checkpoints[usebool]
        amountofhereusepoints =  np.size(hereusepoints, axis=0)
        expandedpoint = np.repeat([point],amountofhereusepoints, axis=0)
        pointtopointvect = proteinpoints - expandedpoint
        zaxis=np.np.repeat(np.array([[0,0,1]]), amountofhereusepoints, axis=0)
        xaxis=np.np.repeat(np.array([[1,0,0]]), amountofhereusepoints, axis=0)
        thetas = angle_between_vectors(pointtopointvect, zaxis)
        phis = angle_between_vectors(pointtopointvect, xaxis)

        #find gaps in the angledistribution


'''


# In[5]:

# General stuff

def calc(instructionsfile, pdbfile, resultsfile, RAMOFMACHINE):

    # read the instructions file
    f = open(instructionsfile, "r")

    line = f.readline()
    line = line.strip()
    (subunitforwork, projectname, functionnumber, angleforworkstart,
     angleforworkend, natext, shortpath) = line.split(",")

    RAMOFMACHINE = float(RAMOFMACHINE)

    f.close()

    #make a directory for the files if not exists yet

    #if (not os.path.exists("files")):
    #    os.makedirs("files")
    #PDB geht von N zu C Terminus

    if shortpath == "1":
        shortpath = True
    else:
        shortpath = False

    UserDefinedProjectName = projectname


    loader.log("There are : " + str(RAMOFMACHINE) + "GB of RAM availible for" +
               " calculation")
    loader.log("Start parsing PDB")

    f = open(pdbfile, 'r')






    wholex = []
    wholey = []
    wholez = []
    wholeatom = []
    wholeaminos = []
    wholesubunit = []
    wholeasnr = []


    # line.split kann nicht verwendet werden, weil manchmal die spalten
    # ineinander verschmelzen, weil das Format doof ist.

    for line in f:
        art = line[:4]
        if art == 'ATOM':
            wholeatom.append(line[13:16])
            wholeaminos.append(line[17:20])
            wholesubunit.append(line[21])
            wholeasnr.append(int(line[22:26]))
            wholex.append(float(line[31:38]))
            wholey.append(float(line[38:46]))
            wholez.append(float(line[46:54]))
        if line[:6] == "ENDMDL":
            break
    f.close()

    # aus allen Listen arrays machen
    wholeatom = np.array(wholeatom)
    wholeaminos = np.array(wholeaminos)
    wholesubunit = np.array(wholesubunit)
    wholeasnr = np.array(wholeasnr)


    differentsubunits = np.unique(wholesubunit)

    # get parts, that aren't wanted out of the PDB files

    #TODO hierüber nachdennken!!! was die Regionen sind, die gewählt werden

    UserChosenIgnoreRegions = None #default is none, being a LIST of tuples of (21, 832, 'A'), with subunit, and then interval including the ends
    IgnoreSubUnit = differentsubunits[differentsubunits != subunitforwork] #is a tupel with to be ignored subunits
    IgnoreIndices = np.bool8(np.ones(np.size(wholeasnr)))

    # Ignoreindices True means the value is kept
    if IgnoreSubUnit is not None:
        for SubUnit in IgnoreSubUnit:
            IgnoreIndices = IgnoreIndices & (wholesubunit != SubUnit)


    if UserChosenIgnoreRegions is not None:
        for RegionOnSubunit in UserChosenIgnoreRegions:
            IgnoreIndices = (IgnoreIndices &
                             np.invert((wholeasnr < RegionOnSubunit[1]) &
                                       (wholeasnr > RegionOnSubunit[0]) &
                                       (wholesubunit == RegionOnSubunit[2])))
    wholeatom = wholeatom[IgnoreIndices]
    wholeaminos = wholeaminos[IgnoreIndices]
    wholesubunit = wholesubunit[IgnoreIndices]
    wholeasnr = wholeasnr[IgnoreIndices]


    wholex = np.float16(np.array(wholex))
    wholey = np.float16(np.array(wholey))
    wholez = np.float16(np.array(wholez))

    # that should be sliced out of the PDB
    wholex = wholex[IgnoreIndices]
    wholey = wholey[IgnoreIndices]
    wholez = wholez[IgnoreIndices]

    anzahl = len(wholex)


    # let the user choose, what part should be circularized interests him.


    SubUnitChosen = subunitforwork
    UserChosenStart = None
    UserChosenEnd = None

    if UserChosenEnd is None:
        UserChosenEnd = np.max(wholeasnr[wholesubunit == SubUnitChosen])

    if UserChosenStart is None:
        UserChosenStart = np.min(wholeasnr[wholesubunit == SubUnitChosen])


    # non helical regions are called scars
    ScarsAtStartseq = "GG"
    ScarsAtStart = len(ScarsAtStartseq)
    ScarsAtEndseq = natext   # TODO richtige Sequenz!
    ScarsAtEnd = len(ScarsAtEndseq)


    MissingAtStart = (np.min(wholeasnr[wholesubunit == SubUnitChosen]) -
                      UserChosenStart)
    MissingAtEnd = UserChosenEnd - np.max(wholeasnr[wholesubunit == SubUnitChosen])

    if MissingAtStart > 0:
        if MissingAtStart >= 5:
            loader.log("Your PDB File does not contain the beginning of the protein and there is missing that much, that even an estimation of the beginning would be really bad. Please find a better PDB file, or risk it")
        else:
            loader.log("Your PDB File does not contain the beginning of the protein, but there are less than 5 Aminoacids missing, so the position of the beginning will be estimated. If there is a better PDB file, upload it")

    if MissingAtEnd > 0:
        if MissingAtEnd >= 5:
            loader.log("Your PDB File does not contain the end of the protein and there is missing that much, that even an estimation of the beginning would be really bad. Please find a better PDB file, or risk it")
        else:
            loader.log("Your PDB File does not contain the end of the protein, but there are less than 5 Aminoacids missing, so the position of the beginning will be estimated. If there is a better PDB file, upload it")


    PartToCircularizeBool = (((wholeasnr >= UserChosenStart) &
                             (wholesubunit == SubUnitChosen)) &
                             (wholeasnr <= UserChosenEnd)) # hier kann man einstellen, welche AS behalten werden sollen.

    InterestingAtom = wholeatom[PartToCircularizeBool]
    InterestingAminos = wholeaminos[PartToCircularizeBool]
    InterestingAANr = wholeasnr[PartToCircularizeBool]

    #aus den drei Arrays eines machen, das Dimension n*3 hat, also ein Array aus lauter kleinen dreier Arrays

    # ein Pkt: pkte[0]
    # wieder zurück: x = pkte[:,0]



    PointsOfAllSubunits = np.float16(np.reshape(np.concatenate((wholex,wholey,wholez)), (anzahl,3), 'F'))
    #choose the part, that is interesting for us for circularization this is points
    pkte = PointsOfAllSubunits[PartToCircularizeBool]
    OtherPoints = PointsOfAllSubunits[wholesubunit != SubUnitChosen]

    # TODO Estimation of startingpoint, or user interface to get it.

    anfangspunkt = np.ravel(pkte[(InterestingAANr == InterestingAANr[0]) & (InterestingAtom == "N  ")])
    endpunkt = np.ravel(pkte[(InterestingAANr == InterestingAANr[-1]) & (InterestingAtom == "C  ")])


    AmountOfAtomsFirstAA = np.size(InterestingAANr[InterestingAANr == InterestingAANr[0]])  #anzahl an Atomen in der erstenas
    AmountOfAtomsLastAA = np.size(InterestingAANr[InterestingAANr == InterestingAANr[-1]])  #amount of atoms in last AS

    loader.log("The protein has in total: " + str(np.size(PointsOfAllSubunits,
                                                          axis=0)) +
               " Points, but only " + str(np.size(pkte, axis=0)) +
               " are between the ends")
    #TODO Winkel einfügen


    # In[7]:

    # this dictionary contains the medium, the standrad-deviation and the sequence of all the angles
    angletosequence = [(29.7, 8.5, "NVL"), (38.7, 30., "KTA"),
                       (60., 12., "AADGTL"), (74.5, 27., "VNLTA"),
                       (117., 12., "AAAHPEA"), (140., 15., "ASLPAA"),
                       (160., 5., "ATGDLA")]
    angleseparators = [0.]

    # the separators are there where the amount of sigmas is
    # the same from both directions
    for i in range(len(angletosequence)-1):
        factor = ((angletosequence[i+1][0] - angletosequence[i][0]) /
                  (angletosequence[i+1][1] + angletosequence[i][1]))
        angleseparators.append(factor * angletosequence[i][1] +
                               angletosequence[i][0])
    angleseparators.append(180.)



    #Längenkalibration, wir wissen, dass der Abstand von c-c 154 pm ist.
    #Wir machen das am Glycin, weil das am einfachsten für uns ist.
    try:
        eichnutz = ((wholeaminos == "GLY") & (wholeatom == "C  ") |
                    ((wholeaminos == "GLY") & (wholeatom == "CA ")))
        xeich = wholex[eichnutz]
        yeich = wholey[eichnutz]
        zeich = wholez[eichnutz]


        #das sieht so komisch aus, wegen alter Version
        abstaendeeich= abstand( np.array([xeich[0::2],yeich[0::2],zeich[0::2]]),np.array([xeich[1::2],yeich[1::2],zeich[1::2]]))
        kalib = 154. / np.mean(abstaendeeich) #pm
        kalibfehl = np.std(abstaendeeich) * kalib

        loader.log(str(kalib) + "+-" +str (kalibfehl) +" pm")
    except:
        kalib = 100.
        kalibfehl = 0.
        loader.log("There were no Glycines in the protein, a calibration was estimated as :" + str(kalib) + "+-" +str (kalibfehl) +" pm")


    # In[10]:

    # globale Variablen:

    # Entfernung, die der Linker mindestens immer haben sollte geschaetzter Wert
    # 5 Angström, eine Alpha Helix hat Radius 2.3A

    minabstand = 500/kalib #in pm

    # Entfernung, die ein Linker maximal haben darf vom Protein

    maxabstand = 5000/kalib

    LengthOfFlexibleAA = 250 / kalib          # between 250 and 350
    FLEXIBLEATSTARTKO = (MissingAtStart + ScarsAtStart) * LengthOfFlexibleAA
    FLEXIBLEATENDKO = (MissingAtEnd + ScarsAtEnd) * LengthOfFlexibleAA


    # Wir testen, ob sich die Enden einfach direkt verbinden lassen. Dafür schauen wir ob auf der Verbindungslinie zwischen den beiden Enden im senkrechten Abstand alle Punkte mindestens einen gewissen Abstand haben. Da aber der Punkteraum diskret ist und nicht ausgeschmiert, schauen wir einfach für jeden Würfel um die Verbindungslinie, welches der geringste Abstand eines Punktes ist. Ist dieser geringer als unser geforderter Mindestabstand, bricht der Algorithmus sofort ab und es kann weiter gehen. Die Würfel sind nur dazu da, dass wir nicht immer den Abstand des gesamten Proteins zur Linie berechnen müssen. Wenn ein Punkt zu nah ist, finden wir ihn so auf jeden Fall.
    #
    # Wir müssen auf jeden Fall den Abstand zwischen zwei Messpunkten so wählen, dass selbst wenn der Punkt am ungünstigsten liegt, wir ihn aussortieren. Lieber zu früh aussortieren als zu spät und dann eben das normale Prozedere durchmachen lassen. Wir wählen die Abstände so, dass immer der nächste Punkt
    #
    # Der erste Messpunkt muss so sein, dass nicht unser Startpunkt in den ersten Würfel fällt, genauso beim letzten.

    # In[11]:

    abstandanfend = abstand(anfangspunkt, endpunkt)
    kantenlaenge = 4 * minabstand
    wuerfeldiaghalbe = np.sqrt(3)/2 * kantenlaenge
    loader.log("508: die Enden sind: " + str(abstandanfend) + " in KO "+
               "auseinander")
    # wir setzen einen mehr ein, als wir müssten
    anzahlwuerfel = int(abstandanfend / wuerfeldiaghalbe)
    if anzahlwuerfel == 0:
        if abstandanfend < (2* minabstand):
            loader.log("The ends are too close")
            return 0
        else:
            wuerfelmitten = np.array([(anfangspunkt-endpunkt)/2])
            kantenlaenge = abstandanfend / np.sqrt(3)
            wuerfelabstand = 0
    elif anzahlwuerfel == 1:
        kantenlaenge = abstandanfend / np.sqrt(3)
        wuerfeldiaghalbe = np.sqrt(3)/2 * kantenlaenge
        wuerfelmitten = ((endpunkt - anfangspunkt) / abstandanfend *
                         (wuerfeldiaghalbe) + anfangspunkt)
        wuerfelabstand = 0

    else:
        wuerfelabstand = ((abstandanfend - (2* wuerfeldiaghalbe)) /
                          (anzahlwuerfel - 1))

        #nun die Verbindungsgerade zwischen den beiden Punkten. v = m * t + 0 mit normiertem m und t (Abstand*parameter)
        wuerfelmitten = []
        for i in range(0, anzahlwuerfel):
            wuerfelmitten.append((endpunkt - anfangspunkt) / abstandanfend * (wuerfelabstand * i + wuerfeldiaghalbe) + anfangspunkt)

        wuerfelmitten = np.array(wuerfelmitten)


    # minimale Abstand, den etwas haben muss, von Würfelmittelpunkt, ab dem wir
    # sagen, dass was zu nah ist, das ist auch
    # der Fehler den wir haben können.
    minabstandcalc = np.sqrt(minabstand**2 + wuerfelabstand**2)

    derallernaechstepunkt = None

    # das Einschränken der Werte auf die Würfelinnereien
    if np.shape(wuerfelmitten) == (3,):
        mitte = wuerfelmitten
        keep = ((PointsOfAllSubunits[:,0] > (mitte[0] - (kantenlaenge / 2))) &
                (PointsOfAllSubunits[:,0] < (mitte[0] + (kantenlaenge / 2))) &
                (PointsOfAllSubunits[:,1] > (mitte[1] - (kantenlaenge / 2))) &
                (PointsOfAllSubunits[:,1] < (mitte[1] + (kantenlaenge / 2))) &
                (PointsOfAllSubunits[:,2] > (mitte[2] - (kantenlaenge / 2))) &
                (PointsOfAllSubunits[:,2] < (mitte[2] + (kantenlaenge / 2))))

        wuerfelpunkte = PointsOfAllSubunits[keep]

        mintemp = np.min(abstandpktzuarray(mitte, wuerfelpunkte))

        if  mintemp < minabstandcalc:
            loader.log("Es ist nicht moeglich einen direkten Linker zu bauen. Der minimale Abstand von der direkten Verbindung betrug: " + str( mintemp * kalib) + " pm")

        else:
            if derallernaechstepunkt is None:
                derallernaechstepunkt = mintemp
            elif mintemp < derallernaechstepunkt:
                derallernaechstepunkt = mintemp

            else:
                loader.log("Es ist möglich einen direkten Linker zu machen, da der nächste Punkt vom Linker " + str(derallernaechstepunkt * kalib) +  " pm entfernt ist.")
    else:

        for mitte in wuerfelmitten:
            keep = ((PointsOfAllSubunits[:,0] > (mitte[0] - (kantenlaenge / 2))) &
                    (PointsOfAllSubunits[:,0] < (mitte[0] + (kantenlaenge / 2))) &
                    (PointsOfAllSubunits[:,1] > (mitte[1] - (kantenlaenge / 2))) &
                    (PointsOfAllSubunits[:,1] < (mitte[1] + (kantenlaenge / 2))) &
                    (PointsOfAllSubunits[:,2] > (mitte[2] - (kantenlaenge / 2))) &
                    (PointsOfAllSubunits[:,2] < (mitte[2] + (kantenlaenge / 2))))

            wuerfelpunkte = PointsOfAllSubunits[keep]

            mintemp = np.min(abstandpktzuarray(mitte, wuerfelpunkte))

            if  mintemp < minabstandcalc:
                loader.log("Es ist nicht moeglich einen direkten Linker zu bauen. Der minimale Abstand von der direkten Verbindung betrug: "                     + str( mintemp * kalib) + " pm")
                break

            else:
                if derallernaechstepunkt is None:
                    derallernaechstepunkt = mintemp
                elif mintemp < derallernaechstepunkt:
                    derallernaechstepunkt = mintemp

        else:
            loader.log("Es ist möglich einen direkten Linker zu machen, da der nächste Punkt vom Linker " + str(derallernaechstepunkt * kalib) +               " pm entfernt ist.")


    #FIXME, der Control Flow... Wenn es vorher feststellt, dass die Enden sehr nah beieinander sind, geht es dennoch durch das ganze
    #untere wieder durch... Mal schauen, was sich da machen lässt.


    # Ob eine Region außen ist. Dafür werden von dem Punkt Strahlen in alle Richtungen in 5° Schritten gemacht und diese dann in eine Liste geschrieben, welche Winkel frei sind.

    # In[12]:
    loader.log("605:loading various functions.")

    def punktebeigerade(minabstand, pkte, gerade, aufpunkt, laenge):
        '''
        checks whether there are points too close to a straight line coming from
        aufpunkt with in direction of gerade with length laenge.

        returns True if no point of pkte is closer to the straight line than
        minabstand
        '''
        kantenlaenge = 4 * minabstand
        wuerfeldiaghalbe = np.sqrt(3)/2 * kantenlaenge

        anzahlwuerfel = int(laenge / wuerfeldiaghalbe) + 1

        #nun die Verbindungsgerade zwischen den beiden Punkten.
        # v = m * t + x0 mit normiertem m und t (Abstand*parameter)
        wuerfelmitten = []

        for i in range(0, anzahlwuerfel):
            wuerfelmitten.append(gerade * (wuerfeldiaghalbe * (i + 1)) + aufpunkt)


        wuerfelmitten = np.array(wuerfelmitten)




        # minimale Abstand, den etwas haben muss, von Würfelmittelpunkt, ab dem wir sagen, dass was zu nah ist
        minabstandcalc = np.sqrt(5) * minabstand

        if np.shape(wuerfelmitten) == (3,):
            mitte = wuerfelmitten
            keep = ((PointsOfAllSubunits[:,0] > (mitte[0] - (kantenlaenge / 2))) &
                    (PointsOfAllSubunits[:,0] < (mitte[0] + (kantenlaenge / 2))) &
                    (PointsOfAllSubunits[:,1] > (mitte[1] - (kantenlaenge / 2))) &
                    (PointsOfAllSubunits[:,1] < (mitte[1] + (kantenlaenge / 2))) &
                    (PointsOfAllSubunits[:,2] > (mitte[2] - (kantenlaenge / 2))) &
                    (PointsOfAllSubunits[:,2] < (mitte[2] + (kantenlaenge / 2))))

            wuerfelpunkte = PointsOfAllSubunits[keep]
            if np.shape(wuerfelpunkte) == (0, 3):
                mintemp = minabstandcalc
            else:
                mintemp = np.min(abstandpktzuarray(mitte, wuerfelpunkte))

            if mintemp < minabstandcalc:
                return False

        # das Einschränken der Werte auf die Würfelinnereien
        else:
            for mitte in wuerfelmitten:
                keep = ((pkte[:, 0] > (mitte[0] - (kantenlaenge / 2))) &
                        (pkte[:, 0] < (mitte[0] + (kantenlaenge / 2))) &
                        (pkte[:, 1] > (mitte[1] - (kantenlaenge / 2))) &
                        (pkte[:, 1] < (mitte[1] + (kantenlaenge / 2))) &
                        (pkte[:, 2] > (mitte[2] - (kantenlaenge / 2))) &
                        (pkte[:, 2] < (mitte[2] + (kantenlaenge / 2))))

                wuerfelpunkte = pkte[keep]
                if np.shape(wuerfelpunkte) == (0, 3):
                    continue
                else:
                    mintemp = np.min(abstandpktzuarray(mitte, wuerfelpunkte))

                    if mintemp < minabstandcalc:
                        return False

        return True

    def test_accessible_angles(winkelarray, length, anfangspunkt,
                               proteinpoints,  gerade=np.array([0, 0, 1])):
        '''
        winkelarray is an array of angles that should be checked, whether they are
        accessible from anfangspunkt. Accessible means that no point of protein-
        points is too close to the straight line, which is produced by rotating
        gerade with the angles of winkelarray. Gerade always starts at anfangspunkt
        angles are measured from z-axis, if gerade is not defined else.

        returns a boolean array with which winkelarray can be sliced.
        '''
        moeglichewinkelanfangbool = []

        for winkel in winkelarray:
            moeglichewinkelanfangbool.append(punktebeigerade(minabstand,
                                                             PointsOfAllSubunits,
                                                             drehenxy(winkel[0],
                                                                      winkel[1],
                                                                      gerade),
                                                             anfangspunkt,
                                                             maxvonanfang))

        return np.array(moeglichewinkelanfangbool)


    def reduce_angles_from_redundancies(winkelarray):
        '''
        takes an array of angles in the format [phi, theta] and looks which angles
        produce the same result in the vector.

        Returns an array with all indices, that can be deleted along the 0 axis
        of winkelarray.
        '''
        winkelvekt = []
        for winkel in winkelarray:
            winkelvekt.append(drehenxy(winkel[0], winkel[1], np.array([0, 0, 1])))

        winkelvekt = np.array(winkelvekt)
        # from stackoverflow, makes object out of line
        deletelist = []
        for i in range(np.shape(winkelvekt)[0]):
            for j in range(np.shape(winkelvekt)[0]):
                if (i != j) & (j not in deletelist) & (i not in deletelist):
                    if (winkelvekt[i] == winkelvekt[j]).all():
                        deletelist.append(i)

        return np.array(deletelist)


    # In[13]:

    # das sind nun 2592 Berechnungen...
    # Endwinkel nicht enthalten, null mit drinnen, das sind nur 70 Rechn extra
    testwinkel = np.mgrid[0:180:5, 0:360:5] * np.pi/180
    winkelarray = np.reshape(np.ravel(testwinkel), (2592, 2), 'F')
    # sort out redundancies in the winkelarray
    winkelarray = np.delete(winkelarray,
                            reduce_angles_from_redundancies(winkelarray), axis=0)


    # Ueberprüfen, ob der Anfang innen ist.
    maxvonanfang = np.max(abstandpktzuarray(pkte[0], PointsOfAllSubunits))

    # geradenarray = np.reshape(np.ravel(drehenxy(testwinkel[0], testwinkel[1], gerade), order = 'F'), (2592,3), 'C')

    moeglichewinkelanfangbool = test_accessible_angles(winkelarray, maxvonanfang,
                                                       anfangspunkt,
                                                       PointsOfAllSubunits)


    # Überprüfen, ob das Ende innen ist.
    maxvonende = np.max(abstandpktzuarray(endpunkt, PointsOfAllSubunits))


    moeglichewinkelendebool = test_accessible_angles(winkelarray, maxvonende,
                                                     endpunkt, PointsOfAllSubunits)



    moeglichewinkelanfang = winkelarray[moeglichewinkelanfangbool]
    moeglichewinkelende = winkelarray[moeglichewinkelendebool]
    if ((np.size(moeglichewinkelanfangbool) == 0) |
       (np.size(moeglichewinkelendebool) == 0)):

        # TODO, vielleicht noch mit flexiblem Linker verbindbar?
        # Einfach der Test, ob es an der Oberfläche ist.
        sys.exit("Exit 0, One end is covered in the protein, it is not" +
                 "circularizable")


    # Wir versuchen nun wirklich einen Linker zu finden. Dafür alle möglichen Linker, die zum Ziel führen erzeugen lassen. So ein Linker ist eindeutig bestimmt, durch die Punkte, durch die er durchgeht, das heißt man muss nur die Punkte abspeichern lassen. Die kann man dann auswerten im Endeffekt und so den besten Linker rausfinden.
    #
    # Dabei kann ein Linker maximal 3 Winkel haben, dann ist es möglich ein 5 Eck mit den Punkten zu bauen. Das ergibt bei einer Winkelvervteilung von jeweils 5 ° 2500^3 Möglichkeiten.
    #
    # Jede Aminosäure in einer Alphahelix macht dann eine Verschiebung um 1,5 Angström. Das heißt, dass jedes einzelne Linkerstück (keine Gelenke) 1.5A lang ist.
    #
    # Für die maximale Länge des Linkers legen wir eine Schnur um eine Kugel, mit dem Radius des 3/4 (noch drüber sprechen) des maximalen Abstands von dem Ende zu dem Rest.
    #
    #

    # Wir sortieren jetzt die Punkte aus, bei denen Proteinpunkte auf der Verbindungslinie zwischen den beiden liegen.
    #
    # Dafür berechnen wir für jede Verbindung zwischen A und B alle Abstände AC und BC. Daraus können wir dann rückschlüsse ziehen, ob es Punkte gibt, die zwischen der Verbindungslinie liegen. Generell gibt es zwei Kriterien, die erfüllt sein müssen:
    #
    # AC und BC müssen kürzer sein als AB (Kreis um jeweils den anderen Punkt)
    # AC + BC muss kleiner als $ \sqrt{AB^2 + d^2}+d$ sein. (Ellipse durch die äußersten Eckpunkte, die wir aussortieren wollen)
    #
    # Mit dieser Methode sortieren wir um ungünstigsten Fall (kürzester Linker, schlechtester Punkt vom Protein, also ganz in der Mitte) noch Punkte aus, bei denen ein Punkt in 2d Entfernung vom Linker ist. Das ist ok, dafür dass das so eine einfache Methode ist.

    # TODO: Irgendwie mit hineinnehmen, ob das Protein groß ist (verschieden lange Linker nehmen), ob man viele Winkel gleich am Anfang angreifen kann (eine Iteration vllt. herausnehmen) und was man so machen kann, um Rechenzeit zu sparen.

    # In[14]:

    # displacement ist wirklich die Verschiebung im 3d raum, deshalb müssen die Längen dreimal draufgemacht werden.
    def make_displacements(lengtharray, displacementarray):
        '''
        generates all possible displacements from displacementarray (an array of
        vectors) and lengtharray (array of different lengths)

        returns an array with displacementvectors in different lengths
        '''
        oneaxis = np.size(lengtharray)
        twoaxis = np.size(displacementarray, axis=0)

        disptiled = np.tile(displacementarray, (oneaxis, 1))
        lengthshaped = np.repeat(lengtharray, 3 * twoaxis)
        lengthshaped = np.reshape(lengthshaped, (oneaxis * twoaxis, 3))

        return disptiled * lengthshaped




    # In[15]:

    def sort_out_by_protein(startingarray, endingarray, proteinpoints, mindist,
                            beforearray = None):
        '''
        sorts out the connections between startingarray and endingarray with pro-
        teinpoints. A connection is sorted out, if one point of the protein-
        points is nearer to the connection, than mindist.

        Returns only the points for the connections, that are good. If beforearray
        is set, returns also beforearray
        '''
        # catch if there is no endingarray
        if np.shape(endingarray) == (3, 0):
            if beforearray is None:
                if np.shape(startingarray) == (3,):
                    return [np.float16(startingarray), np.float16(endingarray)]
                else:
                    return [np.float16(startingarray), np.float16(endingarray)]
            else:
                return (np.float16(beforearray), np.float16(startingarray), np.float16(endingarray))


        if np.shape(startingarray) == (3,):
            starttemp = np.repeat([startingarray], np.size(endingarray, axis=0), axis =0)
        else:
            starttemp = startingarray
        oneaxis = np.size(endingarray, axis=0)
        twoaxis = np.size(proteinpoints, axis=0)
        #expand the arrays
        startendlength = vectabsar(starttemp-endingarray)
        startendlength = np.repeat(startendlength, twoaxis , axis =0)
        starttemp = np.repeat(starttemp, twoaxis, axis =0)#immer die gleichen hintereinander
        endtemp = np.repeat(endingarray, twoaxis, axis =0)
        proteintemp = np.tile(proteinpoints, (oneaxis,1))
        startprotlength = vectabsar(starttemp-proteintemp)
        endprotlength = vectabsar(endtemp-proteintemp)



        #arrays for every connection a row and every proteinpoint a column
        startendlength = np.reshape(startendlength, (oneaxis, twoaxis), "C")
        startprotlength = np.reshape(startprotlength, (oneaxis, twoaxis), "C")
        endprotlength = np.reshape(endprotlength, (oneaxis, twoaxis), "C")

        #make the slicingarray, True means sort out
        connectpointbool = ((startprotlength < startendlength) & (endprotlength < startendlength) &     ((startprotlength + endprotlength) < (np.sqrt(np.square(startendlength)+mindist**2)+mindist)))
        connectpointbool = np.invert(connectpointbool.any(axis = 1) )


        if beforearray == None:
            if np.shape(startingarray) == (3,):
                return [np.float16(startingarray), np.float16(endingarray[connectpointbool])]
            else:
                return [np.float16(startingarray[connectpointbool]), np.float16(endingarray[connectpointbool])]
        else:
            return (np.float16(beforearray[connectpointbool]), np.float16(startingarray[connectpointbool]),                np.float16(endingarray[connectpointbool]))


    # Wir fangen sowohl vorne als auch hinten an, mit allen Winkeln, die möglich sind und allen Längen, die möglich sind. Wir bekommen dann Arrays von den ersten Punkten und den letzten Punkten nach dem Protein.

    # In[16]:

    def naechstepunkte(anfangsarray, verschiebungsarray):
        '''
        generates for each point of anfangsarray, all points that are made by
        displacements of that point with verschiebungsarray.

        Returns two arrays of equal size, the enlarged anfangsarray and the array
        resulting from verschiebungsarray.
        '''
        if ((np.shape(verschiebungsarray) == (3,0)) |
            (np.shape(anfangsarray) == (3,0))):
            return "Exit -2"
        laengeanfang = np.size(anfangsarray, axis=0)
        laengeversch = np.size(verschiebungsarray, axis=0)
        hilfanfang = np.float16(np.repeat(anfangsarray, laengeversch, axis=0))
        hilfversch = np.float16(np.tile(verschiebungsarray, (laengeanfang, 1)))
        return [hilfanfang, hilfanfang + hilfversch]

    def aussortierennachpunken(punktearray, proteinpunkte, minabstand, maxabstand):
        '''
        sorts all the points of punktearray out, that are nearer than minabstand to
        one of the points from proteinpunkte, or farther away than maxabstand.

        returns a boolean array, with which one can slice punktearray.
        '''

        temp1 = np.repeat(punktearray, np.size(proteinpunkte[::4], axis=0), axis =0)
        temp2 = np.tile(proteinpunkte[::4], (np.size(punktearray, axis=0),1))
        abstaende = np.reshape(abstandarrays_quadr(temp1, temp2), (np.size(punktearray, axis=0), np.size(proteinpunkte[::4], axis=0)))
        minimaleabst = np.min(abstaende, axis=1)
        keep = (minimaleabst < maxabstand**2) & (minimaleabst > minabstand**2)
        return keep

    loader.log("903:loading various functions.")

    # In[17]:

    def gaussian_normed(x, sig, mu):
        return 1/(sig*np.sqrt(2*np.pi)) * np.exp(-0.5 * ((x-float(mu))/sig) ** 2)

    # in anglearray there are always the actual angles in it
    # IMPORTANT: here should never be a 0 in it


    def angle_weighing(anglearray, angletosequence=angletosequence):
        '''
        weighting of the angles form anglearray. The better an angle fits to
        the angles provided by angletosequence, the lower the value is.
        The best angle gets a weighing of 1, the worst angle of 2.

        Returns a weighingarray for the angles of anglearray. Each weighing is in
        the range between 1 and 2. The weighing is based on gaussian distributions.
        '''
        # build function
        returnarray = np.zeros(np.size(anglearray))
        sigmas = []
        for angledefinition in angletosequence:
            returnarray = returnarray + gaussian_normed(anglearray, angledefinition[1] * np.pi / 180.,
                                                        angledefinition[0] * np.pi / 180.)
            sigmas.append(angledefinition[1] * np.pi / 180.)
        minsigma = min(sigmas)
        returnarray = 2 / (minsigma * np.sqrt(2 * np.pi)) - returnarray
        return returnarray


    #die Winkelfunktion muss man noch überlegen, in the end it returns a on one normed value.
    def angle_function(StartingArray, MiddleArray, EndingArray):
        '''
        makes a weighing of the connection from Startingarray, over Middlearray to
        Endingarray based on the weighing of the angles.

        Returns an angle weighting for each connection.
        '''
        vect1 = (StartingArray - MiddleArray)
        vect2 = (EndingArray - MiddleArray)
        #catch if there is 0 displacement
        tocalculate = ((vect1 != np.array([0,0,0])).any(1)) & ((vect2 != np.array([0,0,0])).any(1))
        vecttemp1 = vect1[tocalculate]
        vecttemp2 = vect2[tocalculate]
        catchrounding = skalar_product(vecttemp1, vecttemp2)/(vectabsar(vecttemp1)*vectabsar(vecttemp2))
        #get rounding errors
        catchrounding[catchrounding > 1] = 1
        catchrounding[catchrounding < -1] = -1
        angles = np.arccos(catchrounding)
        functionvalues = np.zeros(np.size(MiddleArray, axis=0))
        functionvalues[tocalculate] = angle_weighing(angles)
        return functionvalues

    #needs a on one normed array of the weighing of the points, if not all points are equally weighed

    #TODO: Start can be array or just points, End has to be an array...
    def unpreferable_places(Start, End, ProteinPoints, AminoacidNumberArray,
                            ToBeWeighedAAInput, WeighingofAA, substratelist):
        '''
        Calculates a weighting for the connection from the points of Start to the
        points of End based on the distance from regions that should be omitted.
        These aminoacids should be defined in the ToBeWeighedAAInput array and
        the WeighingofAA array defines how important this region is. If one wants
        whole substrates to be omitted, they should be added in the substratelist.

        returns the weighing of the connections, because of the regions, where the
        linker passes through.

        '''
        if np.shape(Start) == (3,):
            Start = np.repeat([Start], np.size(End, axis=0), axis=0)

        if np.shape(End) == (3,):
            End = np.repeat([End], np.size(Start, axis=0), axis=0)

        #all the normal aminoacids from the arrays
        SliceToBeWeighed = np.in1d(ToBeWeighedAAInput, AminoacidNumberArray)
        ToBeWeighedAA = ToBeWeighedAAInput[SliceToBeWeighed]

        #reduce the points to their mean, so that every aminoacid is equally weighed and not long ones are more important than
        #than short ones
        Points = []
        for number in ToBeWeighedAA:
            Points.append(np.mean(ProteinPoints[AminoacidNumberArray == number], axis=0))
        Points = np.array(Points)

        toappendtoweighingofAA = np.array([])
        #for the substrate
        for sublist in substratelist:
            if sublist[0] in AminoacidNumberArray:
                activepoint = np.mean(ProteinPoints[AminoacidNumberArray == sublist[0]], axis=0)
                boolangles = test_accessible_angles(winkelarray, sublist[1], activepoint, ProteinPoints)
                lengtharray = np.array([0.2, 0.3, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7, 0.8, 1.]) * sublist[2]
                hereangles = winkelarray[boolangles]

                dispnorm = [np.array([0,0,0])]
                for winkel in hereangles:
                    temp = drehenxy(winkel[0], winkel[1], np.array([0,0,1]))
                    np.append(dispnorm, [temp], axis=0)

                disps = make_displacements(lengtharray, dispnorm)
                disps = disps[(disps != np.array([0,0,0])).any(axis = 1)]
                #also add the activesite
                if np.size(Points) == 0:
                    Points = np.concatenate((disps + activepoint, [activepoint]), axis=0)
                else:
                    Points = np.concatenate((Points, disps + activepoint, [activepoint]), axis=0)
                toappendtoweighingofAA = np.append(toappendtoweighingofAA, np.ones(np.size(disps, axis=0) + 1) /
                          (np.size(disps, axis=0) + 1) * sublist[1])


        calc = (Start != End).any(axis = 1)
        Starttemp = Start[calc]
        Endtemp = End[calc]

        DistanceFromConnection, oneaxis, twoaxis = distance_from_connection(Starttemp, Endtemp, Points)


        if WeighingofAA is None:
            WeighingofAA = np.ones(twoaxis)


        #the array is normalized here and gets the size of the points, there can be set in arbitrary numnbers for the weighing
        WeighingofAAtemp = WeighingofAA[SliceToBeWeighed]
        WeighingofAAtemp = np.concatenate((WeighingofAAtemp, toappendtoweighingofAA))
        WeighingofAAtemp = (WeighingofAAtemp/np.mean(WeighingofAAtemp))
        WeighingofAAtemp = np.tile(WeighingofAAtemp, (oneaxis,1))
        WeighingofAAtemp = np.reshape(WeighingofAAtemp, (oneaxis, twoaxis))


        #TODO: zu welcher Potenz soll das dann gehen?
        ValueOfPoint = WeighingofAAtemp / (DistanceFromConnection ** 2)

        returns = np.zeros(np.size(Start, axis=0))
        returns[calc] = np.sum(ValueOfPoint, axis=1)
        return returns


    def distance_from_surface(beforearray, testarray, ProteinPoints, Afterpoint = None):
        '''
        calculates the distances of the testarrays points from the surface as
        just the minimum of the distances to all proteinpoints. It doesn't
        calculate the points that are equal to the points of the beforearray,
        so that these are not taken double. And it checks that the points
        don't lie on the endpoint.

        Returns the weighting of the distance by subtracting mindist, dividing it
        through mindist for making it unitless and then squaring, so that the
        values are better distributed.
        '''
        Horiz_Axis = np.size(ProteinPoints, axis=0)
        testsize = np.size(testarray, axis=0)


        if np.shape(beforearray) == (3,):
            beforearray = np.repeat([beforearray], testsize, axis=0)

        calc = (beforearray != testarray).any(axis = 1)
        if Afterpoint is not None:
            Afterpoint = np.repeat(Afterpoint, testsize, axis=0)
            calc = (Afterpoint != testarray).any(axis = 1) & calc

        FirstPoints = testarray[calc]

        Vert_Axis = np.size(FirstPoints, axis=0)
        Prottemp = np.tile(ProteinPoints, (Vert_Axis, 1))
        if Vert_Axis == 0:
            Distancesret = np.zeros(testsize)
        else:
            Firsttemp = np.repeat(FirstPoints, Horiz_Axis, axis=0)
            Distances = abstandarrays(Firsttemp, Prottemp)
            Distances = np.reshape(Distances, (Vert_Axis, Horiz_Axis))
            Distances = np.min(Distances, axis=1)
            Distancesret = np.zeros(testsize)
            # TODO: Über Potenz nachdenken
            Distancesret[calc] = ((Distances - minabstand) / minabstand) ** 2

        return Distancesret


    def weighing_function_rigids(StartPoint, FirstArray, SecondArray, ThirdArray,
                                 EndPoint, ProteinPoints, AminoacidNumberArray,
                                 ToBeWeighedAA, WeighingofAA=None,
                                 substratelist=None):
        '''
        makes the weighting of rigid linkers, with angle, distance, length and
        regions distribution.

        returns a list of 5 arrays: weighedvalue, normed lenghtweighing,
        Angleweighing, Siteinfluence and the distances
        '''

        LinkerLength = (abstandpktzuarray(StartPoint, FirstArray) +
                        abstandarrays(FirstArray, SecondArray) +
                        abstandarrays(SecondArray, ThirdArray) +
                        abstandpktzuarray(EndPoint, ThirdArray))

        LengthNormed = LinkerLength / (abstand(StartPoint, EndPoint))

        #catch where there are no new points in the SecondArray
        SecondAngles = angle_function(FirstArray, SecondArray, ThirdArray)
        SecondAngles[SecondAngles == 0] = angle_function(StartPoint,
                                                         SecondArray[SecondAngles == 0],
                                                         ThirdArray[SecondAngles == 0])

        Angles = (angle_function(StartPoint, FirstArray, SecondArray) +
                  SecondAngles + angle_function(SecondArray, ThirdArray, EndPoint))

        if ToBeWeighedAA is None:
            SiteInfluenceNormed = np.zeros(np.size(Angles))
        else:
            SiteInfluenceNormed = unpreferable_places(StartPoint, FirstArray,
                                                      ProteinPoints,
                                                      AminoacidNumberArray,
                                                      ToBeWeighedAA,
                                                      WeighingofAA,
                                                      substratelist) + \
            unpreferable_places(FirstArray, SecondArray, ProteinPoints,
                                AminoacidNumberArray, ToBeWeighedAA,
                                WeighingofAA, substratelist) + \
            unpreferable_places(SecondArray, ThirdArray, ProteinPoints,
                                AminoacidNumberArray, ToBeWeighedAA,
                                WeighingofAA, substratelist) + \
            unpreferable_places(EndPoint, ThirdArray, ProteinPoints,
                                AminoacidNumberArray, ToBeWeighedAA,
                                WeighingofAA, substratelist)

        DistancesFromProtein = (distance_from_surface(StartPoint, FirstArray,
                                                      ProteinPoints) +
                                distance_from_surface(FirstArray, SecondArray,
                                                      ProteinPoints) +
                                distance_from_surface(SecondArray, ThirdArray,
                                                      ProteinPoints, [EndPoint]))

        weighedvalue = LengthNormed

        return (weighedvalue, LengthNormed * abstand(StartPoint, EndPoint), Angles,
                SiteInfluenceNormed, DistancesFromProtein)


    def weighing_function_flex(StartPoint, FirstArray, SecondArray, ThirdArray,
                               EndPoint, ProteinPoints, AminoacidNumberArray,
                               ToBeWeighedAA, WeighingofAA = None,
                               substratelist = None):
        '''
        makes the weighting of flexible linkers, with angle, distance, length and
        regions distribution.

        returns a list of 5 arrays: weighedvalue, normed lenghtweighing,
        Angleweighing, Siteinfluence and the distances
        '''

        LinkerLength = (abstandpktzuarray(StartPoint, FirstArray) +
                        abstandarrays(FirstArray, SecondArray) +
                        abstandarrays(SecondArray, ThirdArray) +
                        abstandpktzuarray(EndPoint, ThirdArray))

        LengthNormed = LinkerLength / (abstand(StartPoint, EndPoint))

        Angles = angle_function(FirstArray, SecondArray, ThirdArray)

        if ToBeWeighedAA is None:
            SiteInfluenceNormed = np.zeros(np.size(Angles))
        else:
            SiteInfluenceNormed = unpreferable_places(FirstArray, SecondArray,
                                                      ProteinPoints,
                                                      AminoacidNumberArray,
                                                      ToBeWeighedAA, WeighingofAA,
                                                      substratelist) + \
            unpreferable_places(SecondArray, ThirdArray, ProteinPoints,
                                AminoacidNumberArray, ToBeWeighedAA,
                                WeighingofAA, substratelist)

        DistancesFromProtein = distance_from_surface(FirstArray, SecondArray,
                                                     ProteinPoints)

        weighedvalue = LengthNormed

        return (weighedvalue, LengthNormed * abstand(StartPoint, EndPoint), Angles,
                SiteInfluenceNormed, DistancesFromProtein)
    # Aus dem Weighingstring nutzbare Form machen.


    def make_weighingarrays(Userstring):

        """
    Userstring is of the shape: 273,10 280-290,5 298,7,35.6  etc.
    (spaces separate entries, "," is for single residues "-" for ranges,
    second "," for the diameter of the substrate)

    If nothing should be weighted, insert ""

    returns the information in arrayform (Shouldbeweighed and Weighingarray)
    and a substratelist
        """
        if Userstring == "":
            return None, None, None
        else:
            ShouldBeWeighed = []
            Weighingarray = []
            substratelist = []
            Userlist = Userstring.split()
            for entry in Userlist:
                if "-" not in entry:
                    #- is not in entry
                    if len(entry.split(",")) == 2:
                        ShouldBeWeighed.append(int(entry.split(",")[0]))
                        Weighingarray.append(float(entry.split(",")[1]))
                    else:
                        substratelist.append([int(entry.split(",")[0]), float(entry.split(",")[1]), float(entry.split(",")[2])])
                else:
                    #appends every entry, so borders are included in the interval
                    ShouldBeWeighed += (range(int(entry.split(",")[0].split("-")[0]),int(entry.split(",")[0].split("-")[1])+1))
                    #for many values they should be normed in weighing. it's the sites that interest us, lists are multiplied.
                    Weighingarray += ([float(entry.split(",")[1])/                                       (int(entry.split(",")[0].split("-")[1])+1-int(entry.split(",")[0].split("-")[0]))]*                                      (int(entry.split(",")[0].split("-")[1])+1-int(entry.split(",")[0].split("-")[0])))

            return np.array(ShouldBeWeighed), np.array(Weighingarray), substratelist
    loader.log("1222:loading various functions.")

    # In[18]:

    #TODO die Länge genau bestimmen
    LengthOfAngle = 800 #in pm
    LENGTHOFANGLEKO = LengthOfAngle / kalib
    # hier muss man eintragen, welche Helix-linkerlängen in AS möglich sind.

    linkerdatenbank = np.array(["AEAAAK", "AEAAAKA", "AEAAAKAA", "AEAAAKEAAAK",
                                "AEAAAKEAAAKA", "AEAAAKEAAAKEAAAKA",
                                "AEAAAKEAAAKEAAAKEAAAKA",
                                "AEAAAKEAAAKEAAAKEAAAKEAAAKA"])
    linkerlaengenAS = []

    for i in range(len(linkerdatenbank)):
        linkerlaengenAS.append(len(linkerdatenbank[i]))

    linkerlaengenAS = np.array(linkerlaengenAS)
    linkerlaengenME = linkerlaengenAS * 150 + 2*LengthOfAngle   # in pm
    linkerlaengenKO = linkerlaengenME / kalib           # in koordinaten

    LENGTHACCURACY = 75
    LENGTHACCURACYKO = LENGTHACCURACY / kalib
    # TODO darüber nachdenken, ob 1 wirklich richtig ist.
    SortOutLinkers = linkerlaengenKO < 1*maxvonanfang

    linkerlaengenAS = linkerlaengenAS[SortOutLinkers]
    linkerlaengenME = linkerlaengenME[SortOutLinkers]
    linkerlaengenKO = linkerlaengenKO[SortOutLinkers]
    linkerdatenbank = linkerdatenbank[SortOutLinkers]

    laengstesstueck = np.max(linkerlaengenKO)
    anzahllinker = np.size(linkerlaengenKO)

    maxlinkerAS = int(3 * max(maxvonanfang, maxvonende))    # pi*0.75/1.5 in AS
    maxlinkerKO = maxlinkerAS * 150/kalib
    anzahleckenmax = maxlinkerKO / np.max(linkerlaengenKO)
    anzahleckenmin = abstandanfend / np.min(linkerlaengenKO)

    loader.log("1262: defined different global variables")
    # In[19]:


    def sort_out_by_angle (startingarray, middlearray, endingarray, angletosequence):
        '''
        sorts out the paths from startingarray over middlearray to endingarray.
        A path is sorted out, when the angle it would need is too far away from
        the possible angles in angletosequence

        returns a boolian array which paths to keep, middle and endingarray must
        have same dimension

        If startingarray is only one point, it returns only middlearray and
        endingarray, else all three arrays are returned
        '''
        if ((np.shape(startingarray) == (3, 0)) |
            (np.shape(middlearray) == (3, 0)) |
            (np.shape(endingarray) == (3,0))):
            if np.shape(startingarray) == (3,):
                return middlearray, endingarray
            else:
                return startingarray, middlearray, endingarray

        if np.shape(startingarray) == (3,):
            startingexp = np.repeat([startingarray], np.size(middlearray, axis=0),
                                    axis=0)
        else:
            startingexp = startingarray
        vect1 = (startingexp - middlearray)
        vect2 = (endingarray - middlearray)
        #catch if there is 0 displacement
        tocalculate = ((vect1 != np.array([0,0,0])).any(1)) & ((vect2 != np.array([0,0,0])).any(1))
        if tocalculate.any():
            vect1 = vect1[tocalculate]
            vect2 = vect2[tocalculate]
            catchrounding = skalar_product(vect1, vect2)/(vectabsar(vect1)*vectabsar(vect2))
            #get rounding arrors
            catchrounding[catchrounding > 1] = 1
            catchrounding[catchrounding < -1] = -1
            angles = np.arccos(catchrounding)
            keep = np.bool8(np.zeros(np.size(angles)))
            #here can be defined which angles should be taken into account
            for anglepreferences in angletosequence:
                keep = (keep | ((angles > ((anglepreferences[0]-anglepreferences[1]) * np.pi/180)) &
                               (angles < ((anglepreferences[0]+anglepreferences[1]) * np.pi/180))))

            tempstart = startingexp[tocalculate]
            tempmid = middlearray[tocalculate]
            tempend = endingarray[tocalculate]

            tocalctemp = tocalculate == False
            tempmid = np.concatenate((tempmid[keep], middlearray[tocalctemp]), axis=0)
            tempend = np.concatenate((tempend[keep], endingarray[tocalctemp]), axis=0)

            if np.shape(startingarray) == (3,):
                return (tempmid, tempend)
            else:
                tempstart = np.concatenate((tempstart[keep], startingarray[tocalctemp]), axis=0)
                return tempstart, tempmid, tempend
        else:
            if np.shape(startingarray) == (3,):
                return middlearray, endingarray
            else:
                return startingarray, middlearray, endingarray


    # In[20]:

    def make_small_generator(PointArray, repetition, RAM, tobesplitlength, ProteinArray = None):
        '''
        calculates how often PointArray needs to be split so that the following
        calculations still fit into the RAM.
        RAM in GByte,
        repetition means how often is the largest array repeated

        returns MakeSmall and teiler
        '''

        bytespergig = 1073741824
        AvailableRAM = float(RAM) * bytespergig   # in BytesWaBytesWarning

        try:
            PointSize = PointArray.nbytes
        except:
            # assumes, that it is the size of the array, and this is float 16
            PointSize = PointArray * 2

        if ProteinArray is not None:
            proteinsize = np.size(ProteinArray, axis=0)
        else:
            proteinsize = 1

        UsedMem = PointSize * proteinsize * repetition

        premakesmall = int(UsedMem / AvailableRAM) + 1

        teiler = tobesplitlength / premakesmall

        if teiler != 0:
            MakeSmall = tobesplitlength / teiler
        else:
            MakeSmall = premakesmall
        loader.log("In Make Small RAM: " + str(RAM) +
                   "in GBytes. UsedMem(GB): " + str(UsedMem / bytespergig))
        return MakeSmall, teiler


    def make_small_generator_offset(listofarraysinRAM, PointArray, repetition,
                                    RAM, tobesplitlength,
                                    ProteinArray = None):
        '''
        calculates how often PointArray needs to be split so that the following
        calculations still fit into the RAM.
        In the listofarraysinRAM can be either just the arrays or the size of
        the arrays, same for PointArray
        RAM in GByte,
        repetition means how often is the largest array repeated

        returns MakeSmall and teiler
        '''
        loader.log("MakeSmall started")

        bytespergig = 1073741824
        AvailableRAM = float(RAM) * bytespergig #in BytesWaBytesWarning
        inramsize = 0.
        for array in listofarraysinRAM:
            if array is not None:
                try:
                    inramsize += array.nbytes
                except:
                    inramsize += array * 2 #assumes, that it is the size of the array, and this is float 16
        # print "inramsize" + str(inramsize / 1073741824.)  +"in GB"
                loader.log("1396: arraysize: " + str(np.shape(array)))
                loader.log("1397: size in RAM: " + str(inramsize /
                                                       float(bytespergig)))
        try:
            PointSize = PointArray.nbytes
        except:
            PointSize = PointArray * 2 #assumes, that it is the size of the array, and this is float 16

        loader.log("1400: Pointsize is: " + str(float(PointSize) /
                                                bytespergig))


        if ProteinArray is not None:
            proteinsize = np.size(ProteinArray, axis=0)
        else:
            proteinsize = 1

        loader.log("1413: Protsize is: " + str(float(proteinsize) /
                                        bytespergig))

        UsedMem = PointSize * proteinsize * repetition

        if (AvailableRAM - inramsize) > 0:
            premakesmall = int(UsedMem / (AvailableRAM - inramsize)) + 1
            teiler = tobesplitlength / premakesmall

            if teiler != 0:
                MakeSmall = tobesplitlength / teiler
            else:
                MakeSmall = premakesmall

            loader.log("In Make Small RAM: " + str(RAM) +
                       "in GBytes. UsedMem(GB): " + str(UsedMem / bytespergig)
                        + " so it is dived at points: " + str(teiler))

            return MakeSmall, teiler
        else:
            loader.log("not enough RAM available for next calculation")
            return "Exit -1"

    # In[21]:

    def part_of_RAM(listofarraysinRAM, RAM):
        '''
        returns the part of RAM, that is occupied by the arrays in the
        listofarraysinRAM
        '''

        AvailableRAM = float(RAM) * 1073741824    # in Bytes
        inramsize = 0.
        for array in listofarraysinRAM:
            try:
                inramsize += array.nbytes
            except:
                # assumes, that it is the size of the array, and is float 16
                inramsize += array * 2

        return inramsize / AvailableRAM


    # In[22]:

    # wie genau müssen sich die Stücke treffen wird durch hitgenauig bestimmt,
    # es ist sin(5°) * maximale linkerlänge + einen Helixanteil
    # ~500s

    hitgenauig = 0.0436 * laengstesstueck


    def sort_out_by_distance(startingpoints, endingpoints, firstpoints, distance,
                             variation):
        '''
        generates all possible connections from startingpoints to endingpoints,
        that lie in one of the distances plus minus the variation.

        returns three arrays with all possible paths, made out of all possible combinations startingpoints to endingpoints
        that are in a certain distance
        '''
        if ((np.shape(startingpoints) == (3, 0)) |
            (np.shape(endingpoints) == (3, 0))):
            a = startingpoints
            return a, a, a
        starttemp = np.float16(np.repeat(startingpoints, np.size(endingpoints, axis=0), axis =0))
        endtemp = np.float16(np.tile(endingpoints, (np.size(startingpoints, axis=0),1)))
        abstaende = abstandarrays_quadr(starttemp, endtemp)
        keep = ((abstaende > (distance-variation)**2) & (abstaende < (distance+variation)**2))
        firsttemp = np.float16(np.repeat(firstpoints, np.size(endingpoints, axis=0), axis =0))

        return [firsttemp[keep], starttemp[keep], endtemp[keep]]


    # In[23]:

    def sort_out_by_length (comefrompoints, gotopoints, linkerlaengen):
        '''
        sorts out the connections between comefrompoints and gotopoints, when they
        don't fit to the linkerlengths from linkerlaengen.

        Either comefrompoints or gotopoints can be only one point, but never
        both of them can.

        returns a boolean array, with which you can slice the points, True
        means the values are kept

        '''
        if np.shape(comefrompoints) == (3,0):
            return "Exit -3"
        if np.shape(comefrompoints) == (3,):
            comefrompoints = np.repeat([comefrompoints], np.size(gotopoints, axis=0), axis=0)
        else:
            if np.shape(gotopoints) == (3,):
                gotopoints = np.repeat([gotopoints], np.size(comefrompoints, axis=0), axis=0)

        arraylengthtemp = np.size(comefrompoints, axis=0)
        lonetemp = abstandarrays(comefrompoints, gotopoints)
        #True means keep
        sortouttemp = np.bool8(np.zeros(arraylengthtemp))

        for LAENGE in linkerlaengen:
            sortouttemp = sortouttemp | ((lonetemp < (LAENGE + LENGTHACCURACYKO)) & (lonetemp > (LAENGE - LENGTHACCURACYKO)))

        return sortouttemp

    loader.log("1503:loading various functions.")
    # Gestartet am 9.8. um 15:15 Uhr, 15:55 Uhr bei den Dreieckigen Linkern Versuch eines kompletten Durchlaufs, dann dreistunden für die dreieckigen Linker  Linkerohneeckeflex: 11000 erzeugt, bereits erstmal aussortiert. Linkermiteckeflex:  insgesamt 35000 flexible (also 24000 hinzugekommen)  erstepunkte 2200 erzeugt,  drittepunkte werden 850 000 erzeugt

    # In[288]:

    def length_to_sequence(lengtharray, linkerdatenbank, linkerlaengen):

        '''
        translates the lengthes from lengtharray to sequences according to the
        different linkerpieces in linkerdatenbank.

        returns an array of the sequences that reproduce the length
        '''

        if np.size(lengtharray) == 0:
            return ""
        else:
            #prepare for adding strings always
            addsequencearray = np.zeros(np.size(lengtharray), dtype=str)
            addsequencearray = np.array(addsequencearray, dtype=np.object)

            for i in range(len(linkerlaengen)):
                setseqbool = ((lengtharray >= linkerlaengen[i] - LENGTHACCURACYKO) &
                              (lengtharray <= (linkerlaengen[i] + LENGTHACCURACYKO)))

                addlengtharray = np.repeat(np.array([linkerdatenbank[i]]), np.size(addsequencearray[setseqbool]))
                addsequencearray[setseqbool] = addsequencearray[setseqbool] + addlengtharray

            temp = (addsequencearray == "") & (lengtharray != 0.)
            addsequencearray[temp] = addsequencearray[temp] + "XXX" #TODO nur zum Testen, das muss noch raus!

            return addsequencearray

    def angle_to_sequence(anglearray, angletosequence, angleseparators):

        '''
        translates the angles from anglearray to sequences according to the
        different angletosequence data.

        returns an array of the sequences that reproduce the angles
        '''
        if np.size(anglearray) == 0:
            return ""
        else:

            addsequencearray = np.zeros(np.size(anglearray), dtype=str)
            addsequencearray = np.array(addsequencearray, dtype=np.object)
            anglearraydeg = anglearray / np.pi * 180
            for i in range(len(angletosequence)):
                setseqbool = (anglearraydeg > angleseparators[i]) & (anglearraydeg < angleseparators[i + 1])
                addanglesarray = np.repeat(np.array([angletosequence[i][2]]), np.size(addsequencearray[setseqbool]))
                addsequencearray[setseqbool] = addsequencearray[setseqbool] + addanglesarray
            return addsequencearray

    #returns the weightingarrays and the sequencearrays, concatenated
    def translate_paths_to_sequences(startpoint, firstflex, secondflex, thirdflex,
                                     firstrig, secondrig, thirdrig, endpoint,
                                     linkerdb, linkerlKO, angletosequence,
                                     angleseparators, weightflex, weightrig):

        '''
        translates all paths to sequences according to the patterns provided in
        angleosequence and linkerdb

        returns an array with sequences for each path
        '''
        if (weightflex is not None):
            # flexible linkers
            # initiate the array of objects
            sequenceflex = np.zeros(np.size(firstflex, axis=0), dtype=str)
            sequenceflex = np.array(sequenceflex, dtype=np.object)

            addscarsarray = np.repeat(np.array([ScarsAtStartseq]), np.size(sequenceflex))
            sequenceflex = sequenceflex + addscarsarray

            withoutanglebool = (firstflex == secondflex).all(axis=1)



            firstnoangle = firstflex[withoutanglebool]
            thirdnoangle = thirdflex[withoutanglebool]

            sequenceflex[withoutanglebool] = (sequenceflex[withoutanglebool] +
                                              length_to_sequence(abstandarrays(firstnoangle, thirdnoangle),
                                                                 linkerdb, linkerlKO - (2 * LENGTHOFANGLEKO) ))



            withanglebool = np.invert(withoutanglebool)

            sequenceflex[withanglebool] = sequenceflex[withanglebool] +         length_to_sequence(abstandarrays(firstflex[withanglebool], secondflex[withanglebool]),
                               linkerdb, linkerlKO - LENGTHOFANGLEKO)

            sequenceflex[withanglebool] = sequenceflex[withanglebool] +         angle_to_sequence(angle_between_connections_array(firstflex[withanglebool], secondflex[withanglebool],
                                                              thirdflex[withanglebool]), angletosequence, angleseparators)

            sequenceflex[withanglebool] = sequenceflex[withanglebool] +         length_to_sequence(abstandarrays(secondflex[withanglebool], thirdflex[withanglebool]), linkerdb,
                               linkerlKO - LENGTHOFANGLEKO)

        if weightrig is not None:
            # rigid linkers
            sequencerig = np.zeros(np.size(firstrig, axis=0), dtype=str)
            sequencerig = np.array(sequencerig, dtype=np.object)

            addscarsarray = np.repeat(np.array([ScarsAtStartseq]), np.size(sequencerig))
            sequencerig = sequencerig + addscarsarray


            withoutanglebool = (firstrig == secondrig).all(axis=1)

            withanglebool = np.invert(withoutanglebool)

            sequencerig = sequencerig + length_to_sequence(abstandpktzuarray(startpoint, firstrig) -
                                                           FLEXIBLEATSTARTKO + LENGTHOFANGLEKO,  linkerdb, linkerlKO)
            #split between those from shortpath and those not coming from there
            sequencerig[withanglebool] = (sequencerig[withanglebool] +
                                          angle_to_sequence(angle_between_connections_array(startpoint,
                                                                                            firstrig[withanglebool],
                                                                                            secondrig[withanglebool]),
                                                          angletosequence, angleseparators))

            sequencerig[withanglebool] = (sequencerig[withanglebool] +
                                          length_to_sequence(abstandarrays(firstrig[withanglebool], secondrig[withanglebool]),
                                                             linkerdb, linkerlKO))
            sequencerig[withanglebool] = (sequencerig[withanglebool] +
                                          angle_to_sequence(angle_between_connections_array(firstrig[withanglebool],
                                                                                            secondrig[withanglebool],
                                                                                            thirdrig[withanglebool]),
                                                          angletosequence, angleseparators))

            sequencerig[withoutanglebool] = (sequencerig[withoutanglebool] +
                                          angle_to_sequence(angle_between_connections_array(startpoint,
                                                                                            firstrig[withoutanglebool],
                                                                                            thirdrig[withoutanglebool]),
                                                            angletosequence, angleseparators))


            sequencerig = sequencerig + length_to_sequence(abstandarrays(secondrig, thirdrig), linkerdb, linkerlKO)
            sequencerig = sequencerig + angle_to_sequence(angle_between_connections_array(secondrig, thirdrig, endpoint),
                                                          angletosequence, angleseparators)

            sequencerig = sequencerig + length_to_sequence(abstandpktzuarray(endpoint, thirdrig) -
                                                           FLEXIBLEATENDKO + LENGTHOFANGLEKO,  linkerdb, linkerlKO)


        if weightrig is not None:
            if weightflex is not None:
                sequence = np.concatenate((sequenceflex, sequencerig))
                retweight = np.concatenate((weightflex, weightrig), axis=1)
            else:
                sequence = sequencerig
                retweight = weightrig
        elif weightflex is not None:
            sequence = sequenceflex
            retweight = weightflex
        elif (weightflex is None) & (weightrig is None):
            loader.log( "There were absolutely no linkers found")
            return None, None, None, None, None



        if (weightrig is not None) | (weightflex is not None):
            addscarsarray = np.repeat(np.array([ScarsAtEndseq]), np.size(sequence))
            sequence = sequence + addscarsarray
            if firstrig is not None:
                if firstflex is not None:
                    return sequence , retweight,                np.concatenate((firstflex, firstrig), axis=0),                 np.concatenate((secondflex, secondrig), axis=0),                np.concatenate((thirdflex, thirdrig), axis=0)
                else:
                    return sequence, retweight, firstrig, secondrig, thirdrig
            elif firstflex is not None:
                return sequence, retweight, firstflex, secondflex, thirdflex




        else:
            loader.log("There were absolutely no linkers found, " +
                       "that could be translated to sequences")
            return None, None, None, None, None


    # In[25]:
    loader.log("1685:really starting calculations")
    #wir machen Arrays aus den Verschiebungen, für alle drei auf einmal, alle normiert
    startdisp = np.array([[0,0,0]])
    enddisp = np.array([[0,0,0]])
    dispnorm = np.array([[0,0,0]])
    for winkel in winkelarray:

        temp = drehenxy(winkel[0], winkel[1], np.array([0,0,1]))

        dispnorm = np.append(dispnorm, [temp], axis=0)

        if any((moeglichewinkelanfang[:]==winkel).all(1)):
            startdisp = np.append(startdisp, [temp], axis=0)
        if any((moeglichewinkelende[:]==winkel).all(1)):
            enddisp = np.append(enddisp, [temp], axis=0)


    # Ab hier kann man nach oben starten, wenn es einen Fehler gab.

    # We insert new possible linkers, these are either straight connections between the ends with flexible parts or with maximum one angle in the linker. The point is, that here the flexible ends are estimated better.

    # In[36]:

    #without any edge,
    #+1 because of range
    # restrict the amount of maximally produced first displacements to 4000,
    # otherwise it just calculates too long

    if len(startdisp) > 1000:
        maxnumber = int(4000. / len(startdisp))
        if maxnumber == 1:
            maxnumber = 2
    else:
        maxnumber = 4

    if (ScarsAtStart + MissingAtStart) > 3:
        FLEXATSTART = np.logspace(np.log10(1.5),
                                  np.log10(ScarsAtStart + MissingAtStart),
                                  num=maxnumber) * LengthOfFlexibleAA
    else:
        FLEXATSTART = np.append(np.arange(2, (ScarsAtStart +
                                              MissingAtStart+1)),
                                1.5 ) * LengthOfFlexibleAA

    if len(enddisp) > 1000:
        maxnumber = int(4000. / len(startdisp))
        if maxnumber == 1:
            maxnumber = 2
    else:
        maxnumber = 4

    if (ScarsAtEnd + MissingAtEnd) > 3:
        FLEXATEND = np.logspace(np.log10(1.5),
                                np.log10(ScarsAtEnd + MissingAtEnd),
                                num=maxnumber) * LengthOfFlexibleAA
    else:
        FLEXATEND = np.append(np.arange(2, (ScarsAtEnd + MissingAtEnd+1)), 1.5 ) * LengthOfFlexibleAA


    # The functions start

    # starttime = time.time()
    loader.log("starting pointgeneration")


    if (functionnumber == "1") | (functionnumber == "0"):
        loader.log("function 1 started")

        secondpointsflexible = firstpointsflexible = np.float16(make_displacements(FLEXATSTART, startdisp) + anfangspunkt)
        thirdpointsflexible = np.float16(make_displacements(FLEXATEND, enddisp) + endpunkt)
        loader.log( "firstppointsflex are " + str(np.shape(firstpointsflexible)))
        loader.log( "thirdpointsflex are " + str(np.shape(thirdpointsflexible)))

        amountofthirdpoints = np.size(thirdpointsflexible, axis=0)
        amountofsecondpoints = np.size(secondpointsflexible, axis=0)

        #reduce the amount of points in the protein, that should be checked, as a cylinder around start -> end
        heretousepoints = pkte[np.ravel(distance_from_connection(anfangspunkt, endpunkt, pkte)[0] <  (minabstand + np.max(np.concatenate((FLEXATSTART, FLEXATEND)))))]


        catch = make_small_generator_offset([firstpointsflexible, secondpointsflexible, thirdpointsflexible],
                                            np.size(secondpointsflexible) * np.size(thirdpointsflexible),
                                            2 , RAMOFMACHINE , np.size(secondpointsflexible, axis=0),
                                             ProteinArray=heretousepoints)

        if "Exit" not in catch:
            MakeSmall, teiler = catch
        else:
            loader.log(catch)
            return 0


        for i in range(0,(MakeSmall)):
            loader.log("1748: already " + str(i) + " of " + str(MakeSmall))
            temp1, temp2, temp3 = sort_out_by_distance(secondpointsflexible[:teiler], thirdpointsflexible,
                                        firstpointsflexible[:teiler], abstandanfend, 300 / kalib)
            #300 ist etwa die Hälfte des Unterschieds zwischen zwei Linkerstücken

            firstpointsflexible = np.delete(firstpointsflexible, np.arange(teiler), axis=0)
            secondpointsflexible = np.delete(secondpointsflexible, np.arange(teiler), axis=0)
            keep = (distance_from_connection(temp2, temp3, heretousepoints)[0] >= minabstand).all(axis=1)
            loader.log("still: " + str(np.size(firstpointsflexible, axis=0)) +
                       "to calculate, until function is finished")
            temp1 = temp2 = temp2[keep]
            temp3 = temp3[keep]

            if i == 0:
                firstpointsflexibletemp, secondpointsflexibletemp, thirdpointsflexibletemp = temp1, temp2, temp3
            else:
                firstpointsflexibletemp = np.concatenate((firstpointsflexibletemp, temp1), axis =0)
                secondpointsflexibletemp = np.concatenate((secondpointsflexibletemp, temp2), axis =0)
                thirdpointsflexibletemp = np.concatenate((thirdpointsflexibletemp, temp3), axis =0)

            loader.log("1765: firstpointsflex contains now : " +
                       str( np.size(firstpointsflexibletemp, axis=0)) + "points")
            # catch if the arrays get too large
            if 1 < part_of_RAM([firstpointsflexibletemp,
                                secondpointsflexibletemp,
                                thirdpointsflexibletemp], RAMOFMACHINE):
                loader.log("1803: RAM would overflow by arrays, so stopped " +
                           "further calculations, just continues, with what" +
                           " is already there")
                firstpointsflexible  = firstpointsflexibletemp
                secondpointsflexible = secondpointsflexibletemp
                thirdpointsflexible  = thirdpointsflexibletemp
                break

        if np.shape(firstpointsflexible) != (0,3):
            temp1, temp2, temp3 = sort_out_by_distance(secondpointsflexible, thirdpointsflexible,
                                        firstpointsflexible, abstandanfend, 300 / kalib)

            keep = (distance_from_connection(temp2, temp3, heretousepoints)[0] >= minabstand).all(axis=1)

            temp1 = temp2 = temp2[keep]
            temp3 = temp3[keep]

            firstpointsflexible  = np.concatenate((firstpointsflexibletemp,  temp1), axis =0)
            secondpointsflexible = np.concatenate((secondpointsflexibletemp, temp2), axis =0)
            thirdpointsflexible  = np.concatenate((thirdpointsflexibletemp,  temp3), axis =0)
        else:
            firstpointsflexible  = firstpointsflexibletemp
            secondpointsflexible = secondpointsflexibletemp
            thirdpointsflexible  = thirdpointsflexibletemp

        loader.log("firstppointsflex are finished with " +
                   str(np.shape(firstpointsflexible)) + "points")

        firstpointsflexibletemp = secondpointsflexibletemp = thirdpointsflexibletemp = None

        if functionnumber == "1":

            erstepunkte = None
            zweitepunkte = None
            drittepunkte = None
        loader.log("function 1 finished")



        # In[37]:


        # now it should be tried to link it with one edge in the linker.

    if (functionnumber == "2") | (functionnumber == "0"):
        loader.log( "function 2 started")

        heretousepoints = pkte[abstandpktzuarray( (anfangspunkt + endpunkt) / 2., pkte) < (abstandanfend / 2. +
                                                                                           max(FLEXIBLEATSTARTKO, FLEXIBLEATENDKO))]
        #at about 3h running
        #calculate all the lengths that can produce the distance between beginning and end in an rectangular triangle
        linkertriangle = linkerlaengenKO[(linkerlaengenKO - LENGTHOFANGLEKO) < abstandanfend] - LENGTHOFANGLEKO
        linkertriangleone = np.repeat(linkertriangle, np.size(linkertriangle, axis=0))
        linkertriangletwo = np.tile(linkertriangle, np.size(linkertriangle, axis=0))

        linkertrianglehypoth = np.sqrt(linkertriangleone ** 2 + linkertriangletwo ** 2)

        keeptriangles = ((linkertrianglehypoth > (abstandanfend - FLEXIBLEATENDKO - FLEXIBLEATSTARTKO)) &
                         (linkertrianglehypoth < (abstandanfend + FLEXIBLEATENDKO + FLEXIBLEATSTARTKO)))

        linkertriangleone = linkertriangleone[keeptriangles]
        linkertriangletwo = linkertriangletwo[keeptriangles]

        triangleangles = np.around(np.arctan(linkertriangletwo / linkertriangleone), decimals=2)
        #now we produce all the possible points, that lie on a sphere

        displacements = dispnorm * abstandanfend / 2

        allpointsfortriangles =  (anfangspunkt + endpunkt) / 2. + displacements
        amountoftriangles = np.size(allpointsfortriangles, axis=0)

        anglesintriangle = angle_between_connections_array(np.repeat([endpunkt], amountoftriangles, axis=0),
                                                           np.repeat([anfangspunkt], amountoftriangles, axis=0),
                                                           allpointsfortriangles)
        anglesintriangle = np.around(anglesintriangle, decimals=2)


        allpointsfortriangles = allpointsfortriangles[np.in1d(anglesintriangle, triangleangles)]
        #450 unique points

        #get the displacement angles


        dispnormtribeg = np.array([0,0,0])
        for angle in moeglichewinkelanfang:
            temp = drehenxy(angle[0], angle[1], np.array([0,0,1]))
            dispnormtribeg = np.append(dispnorm, [temp], axis=0)

        dispnormtriend = np.array([0,0,0])
        for angle in moeglichewinkelende:
            temp = drehenxy(angle[0], angle[1], np.array([0,0,1]))
            dispnormtriend = np.append(dispnorm, [temp], axis=0)

        loader.log("1849: linkertrianglesone are " + str(np.shape(linkertriangleone)))
        loader.log("1850: linkertrianglestwo are " + str(np.shape(linkertriangletwo)))

        triangleshiftsbeg = np.float16(make_displacements(FLEXATSTART, dispnormtribeg))


        amountoftriangleshiftsbeg = np.size(triangleshiftsbeg, axis=0)
        triangleshiftsbeg = np.repeat(triangleshiftsbeg, np.size(allpointsfortriangles, axis=0), axis=0)
        allpointsfortriangles = np.tile(allpointsfortriangles, (amountoftriangleshiftsbeg, 1))

        firstpointstriangle  = np.float16(triangleshiftsbeg + anfangspunkt)
        secondpointstriangle = np.float16(triangleshiftsbeg + allpointsfortriangles)

        loader.log( "firstpointstriangle = " + str( np.shape(firstpointstriangle)))
        loader.log("sort triangles out by length now")

        keep = sort_out_by_length(firstpointstriangle, secondpointstriangle, linkertriangle)

        firstpointstriangle = firstpointstriangle[keep]
        secondpointstriangle = secondpointstriangle[keep]
        if keep.any():

            catch = make_small_generator_offset([firstpointstriangle,
                                                 secondpointstriangle],
                                                secondpointstriangle, 12,
                                                RAMOFMACHINE,
                                                np.size(secondpointstriangle, axis=0),
                                                ProteinArray=heretousepoints)

            if "Exit" not in catch:
                MakeSmall, teiler = catch
            else:
                loader.log( catch)
                return -1

            loader.log("bevor anglepoints gemacht sind " + str(MakeSmall) +
                        "Zerteilungen, bei: " + str(teiler))

            #about 250s per MakeSmall run

            for i in range(0, (MakeSmall +1)):
                loader.log("1898: already " + str(i) + " of " + str(MakeSmall))
                if i == MakeSmall:
                    temp1 = firstpointstriangle[i * teiler:]
                    temp2 = secondpointstriangle[i * teiler:]
                else:
                    temp1 = firstpointstriangle[i*teiler:(i+1)*teiler]
                    temp2 = secondpointstriangle[i*teiler:(i+1)*teiler]
                #at first sort all connections out, of which the anglepoint is too near, or too far away from the protein.

                keep = aussortierennachpunken(temp2, heretousepoints, minabstand, maxabstand)

                temp1 = temp1[keep]
                temp2 = temp2[keep]

                #then sort out, if the connection is too near at the protein
                keep = (distance_from_connection(temp1, temp2, heretousepoints)[0] >= minabstand).all(axis=1)

                temp1 = temp1[keep]
                temp2 = temp2[keep]

                if i == 0:
                    firstpointstritemp, secondpointstritemp = temp1, temp2
                else:
                    firstpointstritemp = np.concatenate((firstpointstritemp, temp1), axis =0)
                    secondpointstritemp = np.concatenate((secondpointstritemp, temp2), axis =0)

                loader.log("1915: firstpointstritemp contains now : " +
                       str( np.size(firstpointstritemp, axis=0)) + "points")

            firstpointstriangle = firstpointstritemp
            secondpointstriangle = secondpointstritemp

            loader.log( "firstpointstriangle = " + str( np.shape(firstpointstriangle)))

        # In[32]:

        triangleshiftsend = np.float16(make_displacements(FLEXATEND, dispnormtriend))
        #randomize between the ends and the beginning
        amountoftriangleshiftsbeg = np.size(firstpointstriangle, axis=0)
        amountoftriangleshiftsend = np.size(triangleshiftsend, axis=0)

        triangleshiftsend = np.tile(triangleshiftsend, (amountoftriangleshiftsbeg, 1))
        firstpointstriangle = np.repeat(firstpointstriangle, amountoftriangleshiftsend, axis=0)
        secondpointstriangle = np.repeat(secondpointstriangle, amountoftriangleshiftsend, axis=0)


        # In[ ]:

        thirdpointstriangle  = np.float16(triangleshiftsend + endpunkt)

        loader.log( "firstpointstriangle = " +
                   str( np.shape(firstpointstriangle)))

        keep = sort_out_by_length(secondpointstriangle, thirdpointstriangle, linkertriangle)

        firstpointstriangle = firstpointstriangle[keep]
        secondpointstriangle = secondpointstriangle[keep]
        thirdpointstriangle = thirdpointstriangle[keep]
        if keep.any():
            loader.log( "firstpointstriangle = " + str( np.shape(firstpointstriangle)))


            catch = make_small_generator_offset([firstpointstriangle, secondpointstriangle,
                                                 thirdpointstriangle],
                                                secondpointstriangle, 15, RAMOFMACHINE,
                                                np.size(secondpointstriangle, axis=0),
                                                ProteinArray=heretousepoints)

            if "Exit" not in catch:
                MakeSmall, teiler = catch
            else:
                loader.log( catch)


            # about 250s per MakeSmall run

            for i in range(0, (MakeSmall +1)):
                loader.log("1975: already " + str(i) + " of " + str(MakeSmall))
                if i == MakeSmall:
                    if (i * teiler) < np.size(secondpointstriangle, axis=0):
                        temp1 = firstpointstriangle[i * teiler:]
                        temp2 = secondpointstriangle[i * teiler:]
                        temp3 = thirdpointstriangle[i * teiler:]
                    else:
                        break
                else:
                    temp1 = firstpointstriangle[i*teiler:(i+1)*teiler]
                    temp2 = secondpointstriangle[i*teiler:(i+1)*teiler]
                    temp3 = thirdpointstriangle[i*teiler:(i+1)*teiler]


                # sort out, if the connection is too near at the protein
                keep = (distance_from_connection(temp2, temp3, heretousepoints)[0] >= minabstand).all(axis=1)

                temp1 = temp1[keep]
                temp2 = temp2[keep]
                temp3 = temp3[keep]

                if i == 0:
                    firstpointstritemp, secondpointstritemp, thirdpointstritemp = temp1, temp2, temp3
                else:
                    firstpointstritemp = np.concatenate((firstpointstritemp, temp1), axis =0)
                    secondpointstritemp = np.concatenate((secondpointstritemp, temp2), axis =0)
                    thirdpointstritemp = np.concatenate((thirdpointstritemp, temp3), axis =0)

                loader.log("1765: firstpointstritemp contains now : " +
                       str( np.size(firstpointstritemp, axis=0)) + "points")

        if functionnumber == "2":
            firstpointsflexible  = firstpointstritemp
            secondpointsflexible = secondpointstritemp
            thirdpointsflexible  = thirdpointstritemp
            erstepunkte = None
            zweitepunkte = None
            drittepunkte = None
            loader.log( "finished triangle")

        elif functionnumber == "0":
            firstpointsflexible  = np.concatenate((firstpointstritemp,  firstpointsflexible), axis =0)
            secondpointsflexible = np.concatenate((secondpointstritemp, secondpointsflexible), axis =0)
            thirdpointsflexible  = np.concatenate((thirdpointstritemp,  thirdpointsflexible), axis =0)







        #### Flexible ends estimated to make the same as the rigid parts



        #die verschiebungen mit den Linkerlängen multiplizieren, wichtig ist, in den versch sind immer auch nuller drinnen
    if (functionnumber == "3") | (functionnumber == "0"):
        loader.log("###function 3 started###")
        if functionnumber == "3":
            firstpointsflexible  = None
            secondpointsflexible = None
            thirdpointsflexible  = None




        angleforworkstart = float(angleforworkstart)
        angleforworkend = float(angleforworkend)

        # multiplicate displacements with the linkerlengthes, in the dispnorms always 0 displacements are in there
        versch = make_displacements(linkerlaengenKO, dispnorm)


        anfversch = make_displacements((linkerlaengenKO + FLEXIBLEATSTARTKO -
                                        LENGTHOFANGLEKO), startdisp)
        anfversch = anfversch[(anfversch != np.array([0,0,0])).all(axis=1)]

        endversch = make_displacements((linkerlaengenKO + FLEXIBLEATENDKO -
                                        LENGTHOFANGLEKO), enddisp)
        endversch = endversch[(endversch != np.array([0,0,0])).all(axis=1)]


        #hier werden die Punkte generiert
        erstepunkte = np.float16(naechstepunkte([anfangspunkt], anfversch)[1])
        if "Exit" in erstepunkte:
            loader.log(erstepunkte)
            return 0
        erstepunkte = erstepunkte[(erstepunkte == anfangspunkt).all(axis=1) |
                                  aussortierennachpunken(erstepunkte,
                                                         PointsOfAllSubunits,
                                                         minabstand, maxabstand)]

        letztepunkte = np.float16(naechstepunkte([endpunkt], endversch)[1])
        if "Exit" in letztepunkte:
            loader.log(letztepunkte)
            return 0
        letztepunkte = letztepunkte[(letztepunkte == endpunkt).all(axis=1) |
                                    aussortierennachpunken(letztepunkte, PointsOfAllSubunits, minabstand, maxabstand)]

        # aussortieren, ob Punkte durch Protein gehen
        loader.log("2054:erstepunkte: " + str( np.shape(erstepunkte)))
        loader.log("2055:letztepunkte: " + str( np.shape(letztepunkte)))
        # we just test with all as but not the first and last, because they are too close.

        # TODO hier abfangen, falls gleich alle Punkte weggemacht werden und dann
        # eine Ausgabe machen, dass das ziemlich schwierig
        # und dann aber weiterfortlaufen, das gleiche auch mit den letzten Punkten



        # wir sortieren erstepunkte aus, die zu weit vom Ende entfernt liegen, sodass sie nicht mehr durch
        # die doppelte längste Linkerlänge verbunden werden können

        temp = abstandpktzuarray(endpunkt, erstepunkte)
        keep = temp < (3 * laengstesstueck)
        erstepunkte = erstepunkte[keep]

        # wir sortieren erstepunkte aus, die zu weit vom Ende entfernt liegen,
        # sodass sie nicht mehr durch
        # die doppelte längste Linkerlänge verbunden werden können

        temp = abstandpktzuarray(anfangspunkt, letztepunkte)
        keep = temp < (3 * laengstesstueck)
        letztepunkte = letztepunkte[keep]
        loader.log("2078:erstepunkte: " +str( np.shape(erstepunkte)))
        loader.log("2079:letztepunkte: " +str( np.shape(letztepunkte)))
        #die zweite iteration, erstepunkte wird so groß gemacht, wie zweitepunkte, damit die Wege passen
        #davor fragen wir ab, ob es überhaupt sinnvoll ist, die eine weitere Ecke zu nehmen, das spart viel Rechenzeit

        #Bedingung übedenken!!! DNMT1 in shortpath??? na ja
        if ((np.shape(erstepunkte) == (0, 3)) |
             (np.shape(letztepunkte) == (0, 3))):
            loader.log("Exit 1, not enough starting or endingpoints")
            return 0

        if shortpath:
            zweitepunkte = erstepunkte
        else:
            sliceverschstart = int((np.size(versch, axis = 0) - 1) * (angleforworkstart / 300.))
            if angleforworkend != 300:
                sliceverschend = int((np.size(versch, axis = 0) - 1) * (angleforworkend / 300.))
            else:
                sliceverschend = np.size(versch, axis = 0)

            zweiteiteration = naechstepunkte(erstepunkte, versch[sliceverschstart:sliceverschend])
            zweitepunkte = np.float16(zweiteiteration[1])
            erstepunkte = np.float16(zweiteiteration[0])

        loader.log("3rd points generated")
        loader.log("2103:erstepunkte: "  + str( np.shape(erstepunkte)))
        loader.log("2104:zweitepunkte: " + str( np.shape(zweitepunkte)))
        # Wir sortieren nun alle Winkel aus, die kleiner als 15° sind. Das machen wir aber nicht für die Anfangs und Endpunkte, da nicht klar ist, wie dort die Alphahelix angesetzt wird.

        # In[43]:

        #Nach Winkeln aussortieren, von vorne.

        temp = sort_out_by_angle(anfangspunkt, erstepunkte, zweitepunkte, angletosequence)
        erstepunkte = temp[0]
        zweitepunkte = temp[1]

        if ((np.shape(erstepunkte) == (0, 3)) |
            (np.shape(zweitepunkte) == (0, 3))):
            loader.log("Exit 2, all sorted out by angle")
            return 0

        #wir sortieren zweite Punkte aus, die zu weit vom Ende entfernt liegen, sodass sie nicht mehr durch
        #die doppelte längste Linkerlänge verbunden werden können

        temp = abstandpktzuarray(endpunkt, zweitepunkte)
        keep = temp < (2 * laengstesstueck)
        zweitepunkte = zweitepunkte[keep]
        erstepunkte = erstepunkte[keep]

        if ((np.shape(erstepunkte) == (0, 3)) |
            (np.shape(zweitepunkte) == (0, 3))):
            loader.log("Exit 3, all sorted out distance from end")
            return 0
        # In[46]:

        #Läuft 82 sek, sortiert 60 000 Punkte aus
        #wir sortieren die Punkte aus, die zu weit oder zu nah im Protein sind
        # StartTime = time.time()
        catch = make_small_generator(zweitepunkte,1 , RAMOFMACHINE,
                                     np.size(zweitepunkte, axis=0),
                                     ProteinArray = PointsOfAllSubunits)

        if "Exit" not in catch:
            MakeSmall, teiler = catch
        else:
            loader.log( catch)
            return 0
        loader.log("aussortierennachpunkten gestartet")
        temp = aussortierennachpunken(zweitepunkte[:teiler], PointsOfAllSubunits, minabstand, maxabstand)

        for i in range(1,MakeSmall):
            loader.log("2165: already " + str(i) + " of " + str(MakeSmall))
            temp = np.concatenate((temp, aussortierennachpunken(zweitepunkte[i*teiler:(i+1)*teiler], PointsOfAllSubunits, minabstand, maxabstand)), axis=0)
        if ((i+1) * teiler) < np.size(zweitepunkte, axis=0):
            temp = np.concatenate((temp,
                                   aussortierennachpunken(zweitepunkte[(i+1)*teiler:],
                                   PointsOfAllSubunits, minabstand, maxabstand)),
                                   axis=0)


        # print time.time()-StartTime
        temp = np.array(temp)
        temp = np.ravel(temp, "C")

        zweitepunkte = zweitepunkte[temp]
        erstepunkte = erstepunkte[temp]


        #läuft etwa 11 minuten, reduziert um die Hälfte
        catch = make_small_generator(zweitepunkte, 10 , RAMOFMACHINE ,np.size(zweitepunkte, axis=0),
                                     ProteinArray = PointsOfAllSubunits)


        if "Exit" not in catch:
            MakeSmall, teiler = catch
        else:
            loader.log( catch)

        if ((np.shape(erstepunkte) == (0, 3)) | (np.shape(zweitepunkte) == (0, 3))):
            loader.log("Exit 4, all sorted out by points lying in protein")
            return 0
        loader.log("sort_out_by_prot started, 2nd Points")
        temp = sort_out_by_protein(erstepunkte[:teiler], zweitepunkte[:teiler], PointsOfAllSubunits, minabstand)
        erstetemp = temp[0]
        zweitetemp = temp[1]



        # bla = time.time()
        #das läuft zu lange...
        for i in range(1, MakeSmall):
            loader.log("2199: already " + str(i) + " of " + str(MakeSmall))
            temp = sort_out_by_protein(erstepunkte[i*teiler:(i+1)*teiler], zweitepunkte[i*teiler:(i+1)*teiler], PointsOfAllSubunits, minabstand)

            erstetemp = np.concatenate((erstetemp, temp[0]), axis =0)
            zweitetemp = np.concatenate((zweitetemp, temp[1]), axis =0)
        loader.log("2204:erstetemp: " + str( np.shape(erstetemp)))

        if ((i+1) * teiler) < np.size(zweitepunkte, axis=0):
            temp = sort_out_by_protein(erstepunkte[(i+1)*teiler:], zweitepunkte[(i+1)*teiler:], PointsOfAllSubunits, minabstand)

            erstetemp = np.concatenate((erstetemp, temp[0]), axis=0)
            zweitetemp = np.concatenate((zweitetemp, temp[1]), axis=0)

        erstepunkte = np.float16(erstetemp)
        zweitepunkte = np.float16(zweitetemp)

        if ((np.shape(erstepunkte) == (0, 3)) | (np.shape(zweitepunkte) == (0, 3))):
            loader.log("!!!Exit 5, all sorted out by connections through protein!!!")
            return 0

        loader.log( "erstepunkte: " + str( np.size(erstepunkte, axis=0)))


        # Generierung der Verbindungen zwsichen den zweiten und den dritten Punkten



        catch = make_small_generator(zweitepunkte,8 , RAMOFMACHINE,
                                     np.size(zweitepunkte, axis=0),
                                     ProteinArray=letztepunkte)

        loader.log("###dritte Punkte am Erzeugen###")
        if "Exit" not in catch:
            MakeSmall, teiler = catch
        else:
            loader.log( catch)
            return 0



        #if os.path.exists('files/data{projectname}.h5'.format(projectname = UserDefinedProjectName)):
         #   os.remove('files/data{projectname}.h5'.format(projectname = UserDefinedProjectName))
        #h5f = h5py.File('files/data{projectname}.h5'.format(projectname = UserDefinedProjectName), "w")


        for laenge in linkerlaengenKO:
            loader.log("now at linker: " + str(laenge))
            for i in range(0,(MakeSmall)):

                loader.log("2247: already " + str(i) + " of " + str(MakeSmall))

                temp = sort_out_by_distance(zweitepunkte[i*teiler:(i+1)*teiler],
                                                         letztepunkte,
                                                         erstepunkte[i*teiler:(i+1)*teiler],
                                                                     laenge,
                                                                     hitgenauig)
                if i == 0:
                    erstetemp = temp[0]
                    zweitetemp= temp[1]
                    drittetemp= temp[2]
                else:
                    erstetemp = np.concatenate((erstetemp, temp[0]), axis =0)
                    zweitetemp = np.concatenate((zweitetemp, temp[1]), axis =0)
                    drittetemp = np.concatenate((drittetemp, temp[2]), axis =0)

                    loader.log("2261:erstetemp: " + str( np.shape(erstetemp)))

            if ((i+1) * teiler) < np.size(zweitepunkte, axis=0):
                temp = sort_out_by_distance(zweitepunkte[(i+1)*teiler:],
                                                         letztepunkte,
                                                         erstepunkte[(i+1)*teiler:],
                                                                     laenge,
                                                                     hitgenauig)
                erstetemp = np.concatenate((erstetemp, temp[0]), axis =0)
                zweitetemp = np.concatenate((zweitetemp, temp[1]), axis =0)
                drittetemp = np.concatenate((drittetemp, temp[2]), axis =0)

        erstepunkte = np.float16(erstetemp)
        zweitepunkte = np.float16(zweitetemp)
        drittepunkte = np.float16(drittetemp)

        erstetemp = zweitetemp = drittetemp = None






        #sort out the connections between second and third points by protein.

        #SizeOfArray = len(h5f["dataset_{points}{linker}".format(points = 1, linker = int(laenge))]) * 3

        #removed sizeofarray

        catch = make_small_generator_offset([erstepunkte, zweitepunkte, drittepunkte, firstpointsflexible, secondpointsflexible, thirdpointsflexible],
                                                zweitepunkte, 13 , RAMOFMACHINE ,np.size(zweitepunkte, axis=0),
                                                 ProteinArray = PointsOfAllSubunits)

        if "Exit" not in catch:
            MakeSmall, teiler = catch
        else:
            loader.log( catch)




        #erstepunkte  = h5f["dataset_{points}{linker}".format(points = 1, linker = int(laenge))]
        #zweitepunkte = h5f["dataset_{points}{linker}".format(points = 2, linker = int(laenge))][:teiler]
        #drittepunkte = h5f["dataset_{points}{linker}".format(points = 3, linker = int(laenge))][:teiler]

        temp = sort_out_by_protein(zweitepunkte[:teiler], drittepunkte[:teiler], PointsOfAllSubunits, minabstand, beforearray = erstepunkte[:teiler])
        erstepunkte  = np.delete(erstepunkte, np.arange(teiler), axis = 0)
        zweitepunkte = np.delete(zweitepunkte, np.arange(teiler), axis = 0)
        drittepunkte = np.delete(drittepunkte, np.arange(teiler), axis = 0)
        erstetemp = temp[0]
        zweitetemp = temp[1]
        drittetemp = temp[2]
        loader.log("2329: still " + str(np.size(erstepunkte, axis=0)) +
                       "to calculate, until function is finished")



        #das läuft zu lange, ein Durchlauf 2.5s, das heißt insgesamt: 30500~9hs
        for i in range(1, MakeSmall):
            loader.log("2322: already " + str(i) + " of " + str(MakeSmall))
            #erstepunkte  = h5f["dataset_{points}{linker}".format(points = 1, linker = int(laenge))][i * teiler:(i+1)*teiler]
            #zweitepunkte = h5f["dataset_{points}{linker}".format(points = 2, linker = int(laenge))][i * teiler:(i+1)*teiler]
            #drittepunkte = h5f["dataset_{points}{linker}".format(points = 3, linker = int(laenge))][i * teiler:(i+1)*teiler]
            temp = sort_out_by_protein(zweitepunkte[:teiler], drittepunkte[:teiler], PointsOfAllSubunits, minabstand, beforearray = erstepunkte[:teiler])
            erstepunkte  = np.delete(erstepunkte, np.arange(teiler), axis = 0)
            zweitepunkte = np.delete(zweitepunkte, np.arange(teiler), axis = 0)
            drittepunkte = np.delete(drittepunkte, np.arange(teiler), axis = 0)

            erstetemp = np.concatenate((erstetemp, temp[0]), axis =0)
            zweitetemp = np.concatenate((zweitetemp, temp[1]), axis =0)
            drittetemp = np.concatenate((drittetemp, temp[2]), axis =0)

            loader.log("2349: erstetemp: " + str( np.shape(erstetemp)))

            loader.log("2350: still " + str(np.size(erstepunkte, axis=0)) +
                       "to calculate, until function is finished")

            #erstepunkte  = h5f["dataset_{points}{linker}".format(points = 1, linker = int(laenge))][(i+1) * teiler:]
            #zweitepunkte = h5f["dataset_{points}{linker}".format(points = 2, linker = int(laenge))][(i+1) * teiler:]
            #drittepunkte = h5f["dataset_{points}{linker}".format(points = 3, linker = int(laenge))][(i+1) * teiler:]

        if np.shape(zweitepunkte) != (0,3):
            temp = sort_out_by_protein(zweitepunkte, drittepunkte, PointsOfAllSubunits, minabstand, beforearray = erstepunkte)


            erstetemp = np.concatenate((erstetemp, temp[0]), axis = 0)
            zweitetemp = np.concatenate((zweitetemp, temp[1]), axis = 0)
            drittetemp = np.concatenate((drittetemp, temp[2]), axis = 0)



        erstepunkte = np.float16(erstetemp)
        zweitepunkte = np.float16(zweitetemp)
        drittepunkte = np.float16(drittetemp)

        if ((np.shape(erstepunkte) == (0, 3)) | (np.shape(zweitepunkte) == (0, 3)) |
            (np.shape(drittepunkte) == (0, 3))):
            if functionnumber != "0":
                loader.log("!!!Exit 6, all sorted out by protein!!!")
                return 0

        erstetemp = zweitetemp = drittetemp = None














        #must be before first time get call the points
        try:
            firstpointsflexible
        except NameError:
            firstpointsflexible = None
            secondpointsflexible = None
            thirdpointsflexible = None

        try:
            erstepunkte
        except NameError:
            erstepunkte = None
            zweitepunkte = None
            drittepunkte = None


        # In[53]:

        catch = make_small_generator_offset([firstpointsflexible, secondpointsflexible,
                                             thirdpointsflexible, erstepunkte,
                                             zweitepunkte, drittepunkte], zweitepunkte,
                                            20, RAMOFMACHINE,
                                            np.size(zweitepunkte, axis=0) / (MakeSmall))
        if "Exit" not in catch:
            MakeSmall, teiler = catch
        else:
            loader.log( catch)
            return 0


        if shortpath:
            temp = sort_out_by_angle(anfangspunkt, zweitepunkte[:teiler],
                                     drittepunkte[:teiler], angletosequence)

            erstepunkte = None
            zweitepunkte = np.delete(zweitepunkte, np.arange(teiler), axis=0)
            drittepunkte = np.delete(drittepunkte, np.arange(teiler), axis=0)

            erstetemp = temp[0]
            zweitetemp = erstetemp
            drittetemp = temp[1]
            temp = None
        else:
            temp = sort_out_by_angle(erstepunkte[:teiler], zweitepunkte[:teiler],
                                     drittepunkte[:teiler], angletosequence)

            erstepunkte  = np.delete(erstepunkte, np.arange(teiler), axis=0)
            zweitepunkte = np.delete(zweitepunkte, np.arange(teiler), axis=0)
            drittepunkte = np.delete(drittepunkte, np.arange(teiler), axis=0)

            erstetemp = temp[0]
            zweitetemp = temp[1]
            drittetemp = temp[2]
            temp = None
            loader.log("2431:erstetemp: " + str( np.shape(erstetemp)))
            loader.log("2432:zweitetemp: " + str( np.shape(zweitetemp)))
            loader.log("2432:drittetemp: " + str( np.shape(drittetemp)))


        for i in range(1, MakeSmall):
            loader.log("2437: already " + str(i) + " of " + str(MakeSmall))
            loader.log("2455: still " + str(np.size(zweitepunkte, axis=0)) +
                       "to calculate, until function MakeSmall is finished")
            if shortpath:
                temp = sort_out_by_angle(anfangspunkt, zweitepunkte[:teiler],
                                         drittepunkte[:teiler], angletosequence)
                zweitepunkte = np.delete(zweitepunkte, np.arange(teiler), axis=0)
                drittepunkte = np.delete(drittepunkte, np.arange(teiler), axis=0)

                erstetemp = np.concatenate((erstetemp, temp[0]), axis =0)
                zweitetemp = erstetemp
                drittetemp = np.concatenate((drittetemp, temp[1]), axis=0)
                temp = None
                loader.log("2448:drittetemp: " + str( np.shape(drittetemp)))
            else:
                temp = sort_out_by_angle(erstepunkte[:teiler], zweitepunkte[:teiler],
                                         drittepunkte[:teiler], angletosequence)
                erstepunkte  = np.delete(erstepunkte, np.arange(teiler), axis=0)
                zweitepunkte = np.delete(zweitepunkte, np.arange(teiler), axis=0)
                drittepunkte = np.delete(drittepunkte, np.arange(teiler), axis=0)

                erstetemp = np.concatenate((erstetemp, temp[0]), axis =0)
                zweitetemp = np.concatenate((zweitetemp, temp[1]), axis =0)
                drittetemp = np.concatenate((drittetemp, temp[2]), axis=0)
                temp = None

                loader.log("2461:drittetemp: " + str( np.shape(drittetemp)))

        if shortpath:
            if np.shape(zweitepunkte) != (0,3):
                temp = sort_out_by_angle(anfangspunkt, zweitepunkte, drittepunkte,
                                         angletosequence)
                erstetemp = np.concatenate((erstetemp, temp[0]), axis =0)
                zweitetemp = erstetemp
                drittetemp = np.concatenate((drittetemp, temp[1]), axis=0)
                temp = None
        else:
            if np.shape(zweitepunkte) != (0,3):
                temp = sort_out_by_angle(erstepunkte, zweitepunkte, drittepunkte,
                                         angletosequence)
                erstetemp = np.concatenate((erstetemp, temp[0]), axis=0)
                zweitetemp = np.concatenate((zweitetemp, temp[1]), axis=0)
                drittetemp = np.concatenate((drittetemp, temp[2]), axis=0)
                temp = None


        erstepunkte = np.float16(erstetemp)
        zweitepunkte = np.float16(zweitetemp)
        drittepunkte = np.float16(drittetemp)

        loader.log("###rigid paths all generated###")
        loader.log("2461:erstepunkte: " + str( np.shape(erstepunkte)))





        ###HERE all the generation of linkers is finished.###

        #### Das verbessern der Pfade, anpassen an die Linkerstücke
    Exithere = False
    if functionnumber == "0":
        if ((np.shape(erstepunkte) == (0, 3)) |
            (np.shape(firstpointsflexible) == (0, 3))):
                Exithere = True
    elif (functionnumber == "1") | (functionnumber == "2"):
        if (np.shape(firstpointsflexible) == (0, 3)):
                Exithere = True
    elif functionnumber == "3":
         if (np.shape(erstepunkte) == (0, 3)):
             Exithere = True

    if Exithere:
        loader.log("!!!Exit 7, no linkers anymore to refine!!!")
        return 0
    else:
        loader.log("###not Exithere, started point weighing and translation###")
        #thirdpoints are to be shifted and given back
        def shift_points_to_linkerpatterns(secondpoints, thirdpoints, linkerlaengenKO):

            '''
            shifts thirdpoints to the secondpoints or away from them, so that the distance between second and third fits into the
            patterns that are provided by linkerlaengenKO.
            secondpoints and thirdpoints must have same dimension.

            returns the new thirdpoints

            ATTENTION, changes thirdpoints also
            '''

            lthreetemp = abstandarrays(secondpoints, thirdpoints)
            for LAENGE in linkerlaengenKO:
                if LAENGE == linkerlaengenKO[0]:
                    comparedtopattern = lthreetemp - LAENGE
                else:
                    comparedtopatterntwo = lthreetemp - LAENGE
                    fusionbool = np.abs(comparedtopattern) > np.abs(comparedtopatterntwo)
                    comparedtopattern[fusionbool] = \
                    comparedtopatterntwo[fusionbool].copy()

            toberefinedbool = (np.abs(comparedtopattern) >= LENGTHACCURACYKO)
            thirdpointshere = thirdpoints.copy()
            secondpointshere = secondpoints.copy()
            if toberefinedbool.any():

                toberefinedlengths = comparedtopattern[toberefinedbool]
                arraylengthtemp = np.size(toberefinedlengths)
                shifts = np.zeros(arraylengthtemp)

                # we calculate the shifts, to be sure we shift a bit farther than
                # we need in the end.

                shifts[toberefinedlengths > 0] = (-1 *
                            (toberefinedlengths[toberefinedlengths > 0] -
                             LENGTHACCURACYKO + (LENGTHACCURACYKO / 5.)))

                shifts[toberefinedlengths < 0] = -1 *\
                        (toberefinedlengths[toberefinedlengths < 0] +
                         LENGTHACCURACYKO - (LENGTHACCURACYKO / 5.))

                shifts = np.reshape(np.repeat(shifts, 3), (arraylengthtemp,3))
                lengthestemp = abstandarrays(thirdpointshere[toberefinedbool],
                                             secondpointshere[toberefinedbool])

                lengthestemp = np.reshape(np.repeat(lengthestemp, 3),
                                          (arraylengthtemp, 3))

                thirdpointshere[toberefinedbool] = (((thirdpointshere[toberefinedbool] -
                                   secondpointshere[toberefinedbool]) /
                                    lengthestemp) * shifts) + thirdpointshere[toberefinedbool]

            return thirdpointshere




        def make_better_paths_rigid(startpoint, firstpoints, secondpoints, thirdpoints, endpoint, linkerlaengenKO):
            if np.shape(secondpoints) == (0,3):
                firstpoints = secondpoints = thirdpoints = None
                return firstpoints, secondpoints, thirdpoints
            else:
                '''
                makes all the shiftings that should be needed in the rigid linkers,
                so that they can be easily translated in the end.

                returns:
                firstpoints, secondpoints, thirdpoints
                '''
                linkerlaengenKOtemp = np.append(linkerlaengenKO, 0.)
                # lonetemp = abstandpktzuarray(startpoint, firstpoints)

                # arraylengthtemp = np.size(lonetemp)
                #True bleibt

                keep = sort_out_by_length(startpoint, firstpoints, linkerlaengenKOtemp
                + FLEXIBLEATSTARTKO - LENGTHOFANGLEKO)
                firstpointshere = (firstpoints[keep]).copy()
                secondpointshere = (secondpoints[keep]).copy()
                thirdpointshere = (thirdpoints[keep]).copy()

                thirdpointshere = shift_points_to_linkerpatterns(secondpointshere,
                                                                 thirdpointshere,
                                                                 linkerlaengenKOtemp)

                keep = sort_out_by_length(thirdpointshere, endpoint, linkerlaengenKO +
                                          FLEXIBLEATENDKO - LENGTHOFANGLEKO)
                firstpointshere = firstpointshere[keep]
                secondpointshere = secondpointshere[keep]
                thirdpointshere = thirdpointshere[keep]

                return (firstpointshere.copy(), secondpointshere.copy(),
                        thirdpointshere.copy())


        def make_better_paths_flex(firstpoints, secondpoints, thirdpoints,
                                   endpoint, linkerlaengenKO):
            if np.shape(firstpoints) == (0,3):
                firstpoints = secondpoints = thirdpoints = None
                return firstpoints, secondpoints, thirdpoints
            else:

                linkerlaengenKOtemp = np.append(linkerlaengenKO, 0)

                noanglebool = (firstpoints == secondpoints).all(1)

                firstpointshere = (firstpoints[noanglebool]).copy()
                secondpointshere = (secondpoints[noanglebool]).copy()
                thirdpointshere = (thirdpoints[noanglebool]).copy()

                thirdpointshere = shift_points_to_linkerpatterns(secondpointshere,
                                                                 thirdpointshere,
                                                                 linkerlaengenKOtemp -
                                                                 (2 * LENGTHOFANGLEKO))

                #keep Trues
                arraylengthtemp = np.size(noanglebool)
                sortouttemp = np.bool8(np.ones(arraylengthtemp))
                sortouttemp[noanglebool] = (abstandpktzuarray(endpoint,
                                                              thirdpointshere) <
                                            FLEXIBLEATENDKO)

                return (firstpointshere[sortouttemp].copy(),
                        secondpointshere[sortouttemp].copy(),
                        thirdpointshere[sortouttemp].copy())


        # In[91]:

        loader.log("###all functions loaded, now refining paths###")

        if firstpointsflexible is not None:
            if np.shape(firstpointsflexible != (0, 3)):


                catch = make_small_generator_offset([firstpointsflexible,
                                                     secondpointsflexible,
                                                     thirdpointsflexible,
                                                     erstepunkte,
                                                     zweitepunkte,
                                                     drittepunkte],
                                                     secondpointsflexible, 20 ,
                                                     RAMOFMACHINE,
                                                     np.size(secondpointsflexible,
                                                             axis=0))

                if "Exit" not in catch:
                    MakeSmall, teiler = catch
                else:
                    loader.log( catch)




                temp = make_better_paths_flex(firstpointsflexible[:teiler],
                                              secondpointsflexible[:teiler],
                                              thirdpointsflexible[:teiler],
                                              endpunkt, linkerlaengenKO)

                firstpointsflexible  = np.delete(firstpointsflexible,
                                                 np.arange(teiler), axis=0)
                secondpointsflexible = np.delete(secondpointsflexible,
                                                 np.arange(teiler), axis=0)
                thirdpointsflexible  = np.delete(thirdpointsflexible,
                                                 np.arange(teiler), axis=0)

                firsttemp = temp[0]
                secondtemp = temp[1]
                thirdtemp = temp[2]


                for i in range(1, MakeSmall):
                    loader.log("2685: already " + str(i) + " of " + str(MakeSmall))
                    loader.log("2705: still " +str(np.size(firstpointsflexible,
                                                        axis=0)) +
                       "to calculate, until MakeSmall is finished")
                    # loader.log( str(time.time() - starttime ) + "_at run " + str(i) + "of" + str(MakeSmall)
                    temp = make_better_paths_flex(firstpointsflexible[:teiler],
                                                  secondpointsflexible[:teiler],
                                                  thirdpointsflexible[:teiler],
                                                  endpunkt, linkerlaengenKO)
                    firstpointsflexible  = np.delete(firstpointsflexible,
                                                     np.arange(teiler), axis=0)
                    secondpointsflexible = np.delete(secondpointsflexible,
                                                     np.arange(teiler), axis=0)
                    thirdpointsflexible  = np.delete(thirdpointsflexible,
                                                     np.arange(teiler), axis=0)

                    firsttemp = np.concatenate((firsttemp, temp[0]), axis =0)
                    secondtemp = np.concatenate((secondtemp, temp[1]), axis =0)
                    thirdtemp = np.concatenate((thirdtemp, temp[2]), axis=0)

                if np.shape(firstpointsflexible) != (0, 3):
                    temp = make_better_paths_flex(firstpointsflexible,
                                                  secondpointsflexible,
                                                  thirdpointsflexible,
                                                  endpunkt, linkerlaengenKO)

                    firsttemp = np.concatenate((firsttemp, temp[0]), axis=0)
                    secondtemp = np.concatenate((secondtemp, temp[1]), axis=0)
                    thirdtemp = np.concatenate((thirdtemp, temp[2]), axis=0)


                firstpointsflexible = np.float16(firsttemp)
                secondpointsflexible = np.float16(secondtemp)
                thirdpointsflexible = np.float16(thirdtemp)

                # clear var.
                firsttemp = secondtemp = thirdtemp = None



        if erstepunkte is not None:
            if np.shape(erstepunkte) != (0, 3):
                catch = make_small_generator_offset([firstpointsflexible,
                                                     secondpointsflexible,
                                                     thirdpointsflexible,
                                                     erstepunkte, zweitepunkte,
                                                     drittepunkte], zweitepunkte,
                                                    20, RAMOFMACHINE,
                                                    np.size(zweitepunkte, axis=0))

                if "Exit" not in catch:
                    MakeSmall, teiler = catch
                else:
                    loader.log( catch)
                    return -1


                temp = make_better_paths_rigid(anfangspunkt, erstepunkte[:teiler],
                                               zweitepunkte[:teiler],
                                               drittepunkte[:teiler],
                                               endpunkt, linkerlaengenKO)


                erstepunkte  = np.delete(erstepunkte, np.arange(teiler), axis=0)
                zweitepunkte = np.delete(zweitepunkte, np.arange(teiler), axis=0)
                drittepunkte = np.delete(drittepunkte, np.arange(teiler), axis=0)

                erstetemp = temp[0]
                zweitetemp = temp[1]
                drittetemp = temp[2]


                for i in range(1, MakeSmall):
                    loader.log("2755: already " + str(i) + " of " + str(MakeSmall))
                    loader.log("2705: still " + str(np.size(erstepunkte,
                                                        axis=0)) +
                       "to calculate, until MakeSmall is finished")

                    temp = make_better_paths_rigid(anfangspunkt, erstepunkte[:teiler], zweitepunkte[:teiler], drittepunkte[:teiler],
                                                   endpunkt, linkerlaengenKO)
                    erstepunkte  = np.delete(erstepunkte, np.arange(teiler), axis=0)
                    zweitepunkte = np.delete(zweitepunkte, np.arange(teiler), axis=0)
                    drittepunkte = np.delete(drittepunkte, np.arange(teiler), axis=0)

                    erstetemp = np.concatenate((erstetemp, temp[0]), axis=0)
                    zweitetemp = np.concatenate((zweitetemp, temp[1]), axis=0)
                    drittetemp = np.concatenate((drittetemp, temp[2]), axis=0)


                if np.shape(erstepunkte) != (0,3):
                    temp = make_better_paths_rigid(anfangspunkt, erstepunkte, zweitepunkte, drittepunkte, endpunkt, linkerlaengenKO)
                    erstetemp = np.concatenate((erstetemp, temp[0]), axis=0)
                    zweitetemp = np.concatenate((zweitetemp, temp[1]), axis=0)
                    drittetemp = np.concatenate((drittetemp, temp[2]), axis=0)


                erstepunkte = np.float16(erstetemp)
                zweitepunkte = np.float16(zweitetemp)
                drittepunkte = np.float16(drittetemp)

                erstetemp = zweitetemp = drittetemp = None





        #### Die Bewertungsfunktion

        # Wir definieren Regionen, die schlecht für den Linker sind. Dabei bekommt jede Region eine Güte. Diese Güte sagt, wenn wir einen Linker in einem Abstand von Güte geteilt durch Minabstand vorbeigehen lassen. Das heißt je kleiner die Güte, desto näher kann ich an diesem Punkt vorbei gehen.
        #
        # Im Allgemeinen möchte ich, dass einfach immer die verschiedenen Teile gleich wichtig sind, egal wie groß das Protein ist, oder wie viele Regionen wir da gesagt haben, dass umgangen werden sollen.
        #
        # Bei den Winkeln haben wir ja immer maximal drei Winkel, von dem her, muss das nicht normiert werden.
        #
        # Bei der Länge wird mit dem Abstand der Enden skaliert, bei den unguten Regionen wird so skaliert, dass egal wie viele es sind, die definiert wurden, immer insgesamt die Gewichtung 1 ist.

        # In[56]:

        #Userstring ist von der Form: 273,10 280-290,5 298,7,35.6  usw. (Leerzeichen trennen Einträge, , for single residues
        #- for ranges, second, for the diameter of the substrate)



        #UserdefinedWeighing = "19,10,10" #Lambdalysozyme
        UserdefinedWeighing = ""

        loader.log("###weighting started###")

        ShouldBeWeighed, Weighingarray, substratelist = make_weighingarrays(UserdefinedWeighing)

        #weighting of linkers with flexible ends

        if secondpointsflexible is not None:
            if np.size(secondpointsflexible, axis=0) > 0 :
                loader.log("2876: flexible weighting")

                catch = make_small_generator_offset([firstpointsflexible,
                                                     secondpointsflexible,
                                                     thirdpointsflexible,
                                                     erstepunkte, zweitepunkte,
                                                     drittepunkte],
                                                    secondpointsflexible, 8 ,
                                                    RAMOFMACHINE,
                                                    np.size(secondpointsflexible,
                                                            axis=0),
                                                    ProteinArray=pkte)

                if "Exit" not in catch:
                    MakeSmall, teiler = catch
                else:
                    loader.log( catch)
                    return 0




                temp = weighing_function_flex(anfangspunkt, firstpointsflexible[:teiler], secondpointsflexible[:teiler],
                                                thirdpointsflexible[:teiler], endpunkt, pkte, InterestingAANr,\
                                      ShouldBeWeighed, Weighingarray, substratelist)

                knull = temp[0]
                keins = temp[1]
                kzwei = temp[2]
                kdrei = temp[3]
                kvier = temp[4]
                loader.log("2907: first weightingstep finished")


                for i in range(1, MakeSmall):
                    loader.log("2855: already " + str(i) + " of " + str(MakeSmall))
                    temp = weighing_function_flex(anfangspunkt, firstpointsflexible[i * teiler:(i+1)*teiler],
                                                    secondpointsflexible[i * teiler:(i+1)*teiler],
                                                    thirdpointsflexible[i * teiler:(i+1)*teiler],
                                                    endpunkt, pkte, InterestingAANr, ShouldBeWeighed, Weighingarray, substratelist)

                    knull = np.concatenate((knull, temp[0]), axis =0)
                    keins = np.concatenate((keins, temp[1]), axis =0)
                    kzwei = np.concatenate((kzwei, temp[2]), axis =0)
                    kdrei = np.concatenate((kdrei, temp[3]), axis =0)
                    kvier = np.concatenate((kvier, temp[4]), axis =0)



                if ((i+1) * teiler) < np.size(secondpointsflexible, axis=0):
                    temp = weighing_function_flex(anfangspunkt, firstpointsflexible[(i+1)*teiler:],
                                                    secondpointsflexible[(i+1)*teiler:], thirdpointsflexible[(i+1)*teiler:],
                                                    endpunkt, pkte, InterestingAANr, ShouldBeWeighed, Weighingarray, substratelist)


                    knull = np.concatenate((knull, temp[0]), axis =0)
                    keins = np.concatenate((keins, temp[1]), axis =0)
                    kzwei = np.concatenate((kzwei, temp[2]), axis =0)
                    kdrei = np.concatenate((kdrei, temp[3]), axis =0)
                    kvier = np.concatenate((kvier, temp[4]), axis =0)




                loader.log("3012: flex weighting done")
                weightflex = np.array([knull, keins, kzwei, kdrei, kvier])
                flexk = weightflex
            else:
                loader.log("no linkers")
                weightflex = None
        else:
            weightflex = None


        # In[58]:

        if erstepunkte is not None:
            # weighting of linkers without flexible ends
            if np.size(zweitepunkte, axis=0) > 0:
                loader.log("2876: rigid weighting")

                catch = make_small_generator_offset([firstpointsflexible,
                                                     secondpointsflexible,
                                                     thirdpointsflexible,
                                                     erstepunkte, zweitepunkte,
                                                     drittepunkte], zweitepunkte, 8,
                                                    RAMOFMACHINE,
                                                    np.size(zweitepunkte, axis=0),
                                                    ProteinArray=pkte)

                if "Exit" not in catch:
                    MakeSmall, teiler = catch
                else:
                    loader.log( catch)
                    return -1

                temp = weighing_function_rigids(anfangspunkt, erstepunkte[:teiler], zweitepunkte[:teiler],
                                                drittepunkte[:teiler], endpunkt, pkte, InterestingAANr,\
                                      ShouldBeWeighed, Weighingarray, substratelist)

                knull = temp[0]
                keins = temp[1]
                kzwei = temp[2]
                kdrei = temp[3]
                kvier = temp[4]
                loader.log("2907: first weightingstep finished")


                for i in range(1, MakeSmall):
                    loader.log("2917: already " + str(i) + " of " + str(MakeSmall))
                    temp = weighing_function_rigids(anfangspunkt, erstepunkte[i * teiler:(i+1)*teiler],
                                                    zweitepunkte[i * teiler:(i+1)*teiler],
                                                    drittepunkte[i * teiler:(i+1)*teiler],
                                                    endpunkt, pkte, InterestingAANr, ShouldBeWeighed, Weighingarray, substratelist)

                    knull = np.concatenate((knull, temp[0]), axis =0)
                    keins = np.concatenate((keins, temp[1]), axis =0)
                    kzwei = np.concatenate((kzwei, temp[2]), axis =0)
                    kdrei = np.concatenate((kdrei, temp[3]), axis =0)
                    kvier = np.concatenate((kvier, temp[4]), axis =0)


                if ((i+1) * teiler) < np.size(zweitepunkte, axis=0):
                    temp = weighing_function_rigids(anfangspunkt, erstepunkte[(i+1)*teiler:],
                                                    zweitepunkte[(i+1)*teiler:], drittepunkte[(i+1)*teiler: ],
                                                    endpunkt, pkte, InterestingAANr, ShouldBeWeighed, Weighingarray, substratelist)


                    knull = np.concatenate((knull, temp[0]), axis =0)
                    keins = np.concatenate((keins, temp[1]), axis =0)
                    kzwei = np.concatenate((kzwei, temp[2]), axis =0)
                    kdrei = np.concatenate((kdrei, temp[3]), axis =0)
                    kvier = np.concatenate((kvier, temp[4]), axis =0)



                loader.log("3012: rigid weighting done")
                weightrig = np.array([knull, keins, kzwei, kdrei, kvier])
                temp = None
                knull = keins = kzwei = kdrei = kvier = None
                #k = weightrig
            else:
                weightrig = None
        else:
            weightrig = None


        # At first the different linkers are just analysed. Of course this could be done in the weighing step before, but this is not that calculation intensive and like this it is much more clear when it does what.

        # In[289]:
        loader.log("now translating paths to sequences")
        sequences, weightingsall, firstpointsall, secondpointsall, thirdpointsall \
        =translate_paths_to_sequences(anfangspunkt,firstpointsflexible,
                                      secondpointsflexible, thirdpointsflexible,
                                      erstepunkte, zweitepunkte, drittepunkte,
                                      endpunkt, linkerdatenbank, linkerlaengenKO,
                                      angletosequence, angleseparators, weightflex,
                                      weightrig)
        if sequences is None:
            loader.log("no paths could be translated")
            return 0
        loader.log("3037: finished translation, writing file")
        # loader.log( str(time.time() - starttime ) + "write file"
        f = open(resultsfile, "w")

        f.write("sequence,erstepunkteallx,erstepunkteally,erstepunkteallz,zweitepunkteallx,zweitepunkteally,zweitepunkteallz,drittepunkteallx,drittepunkteally,drittepunkteallz,lengthofpath,weightingofangles,unpreferableplaces,distfromsurface\n")
        for i in range(np.size(sequences)):
            writestring = sequences[i]
            for j in range(3):
                writestring += "," + str(firstpointsall[i][j])
            for j in range(3):
                writestring += "," + str(secondpointsall[i][j])
            for j in range(3):
                writestring += "," + str(thirdpointsall[i][j])
            for j in range(1,5):
                writestring += "," + str(weightingsall[j][i])
            writestring += "\n"

            f.write(writestring)


        f.close()
        loader.log("resultfile written successfully, thank you")