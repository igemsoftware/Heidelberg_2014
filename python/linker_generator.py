
# coding: utf-8

#einlesen des PDB files. die Dateien sollten in proteine gespeichert werden
import numpy as np
#import cPickle as pickle       #zum Zwischenspeichern vor Abstürzen, um Zeit zu sparen.
import h5py                    #zum Zwischenspeichern der Ergebnisse in der Generation der neuen Punkte
import sys                      #kann man vielleicht durch os erstetzen, wird nur für exit gebraucht
#das kann vielleicht noch raus
import os                      #spaßige Dinge mit dem Betriebssystem, z.B. ob ein File existiert



#Betrag eines Vektors
def vectabs(x0, x1, x2):
    return np.sqrt(x0**2 + x1**2 + x2*2)

def vectabsar(ar):
    return np.sqrt(ar[:,0]**2+ar[:,1]**2+ar[:,2]**2)

#gibt normalenvektor zu ebene von drei Punkten aus, bereits normiert
def ebene(a, b, c):
    x0 = (a-b)[1]*(c-b)[2]-((a-b)[2]*(c-b)[1])
    x1 = (a-b)[2]*(c-b)[0]-((a-b)[0]*(c-b)[2])
    x2 = (a-b)[0]*(c-b)[1]-((a-b)[1]*(c-b)[0])
    
    xabs = vectabs(x0, x1, x2)
    
    return np.array([x0/xabs, x1/xabs, x2/xabs])

#einen Vektor mit Drehmatrix drehen um a-achse
def drehenx(phi, x, y, z):
    x1 = x * np.cos(phi * 0)
    y1 = y * np.cos(phi) - z * np.sin(phi)
    z1 = y * np.sin(phi) + z * np.cos(phi)
    return np.array([x1, y1, z1])

def dreheny(phi, x, y, z):
    x1 = x  * np.cos(phi) - z * np.sin(phi)
    y1 = y * np.cos(phi * 0)
    z1 = x * np.sin(phi) + z * np.cos(phi)
    return np.array([x1, y1, z1])

def drehenz(phi, x, y, z):
    x1 = x  * np.cos(phi) - y * np.sin(phi)
    y1 = x * np.sin(phi) +  y* np.cos(phi)
    z1 = z * np.cos(phi * 0)
    return np.array([x1, y1, z1])


def drehenxy(phi, theta, v):
    '''
    dreht Vektor v (als np.array) um phi um die x-Achse, und theta um die y-Achse
    '''
    v = drehenx(phi, v[0], v[1], v[2])
    return dreheny(theta, v[0], v[1], v[2])

def abstand(x,y):
    '''
    den Abstand zweier Punkte bestimmen, den Punkt als Array eingeben.
    '''
    return np.sqrt((x[0]-y[0])**2+(x[1]-y[1])**2+(x[2]-y[2])**2)

def betrag(x):
    return np.sqrt((x[0])**2+(x[1])**2+(x[2])**2)

def abstandpktzuarray(x, ar):
    return np.sqrt((x[0]-ar[:,0])**2+(x[1]-ar[:,1])**2+(x[2]-ar[:,2])**2)

def abstandarrays(ar1, ar2):
    return np.sqrt((ar1[:,0]-ar2[:,0])**2+(ar1[:,1]-ar2[:,1])**2+(ar1[:,2]-ar2[:,2])**2)

def abstandarrays_quadr(ar1, ar2):
    return (ar1[:,0]-ar2[:,0])**2+(ar1[:,1]-ar2[:,1])**2+(ar1[:,2]-ar2[:,2])**2

def skalar_product (ar1, ar2):
    return (ar1[:,0]*ar2[:,0])+(ar1[:,1]*ar2[:,1])+(ar1[:,2]*ar2[:,2])


def angle_between_connections_array(StartArray, MiddleArray, EndArray):
    '''
    returns value between [0,pi] an array of size Startarray with the angles. If there is no displacement, it returns zero as value
    '''
    vect1 = (StartArray - MiddleArray)
    vect2 = (EndArray - MiddleArray)
    #catch if there is 0 displacement
    tocalculate = ((vect1 != np.array([0,0,0])).any(1)) & ((vect2 != np.array([0,0,0])).any(1))
    vect1 = vect1[tocalculate]
    vect2 = vect2[tocalculate]
    catchrounding = skalar_product(vect1, vect2)/(vectabsar(vect1)*vectabsar(vect2))
    #get rounding arrors
    catchrounding[catchrounding > 1] = 1
    catchrounding[catchrounding < -1] = -1
    angles = np.arccos(catchrounding)
    returnangles = np.zeros(np.size(StartArray, axis = 0))
    returnangles[tocalculate] = angles
    return returnangles

        
   
def distance_from_connection(Startarray, Endarray, Points):
    '''
takes a connection from Startarray to Endarray nnd calculates the perpendicular distance of the points from the connection. 
Returns an array of size (start * points) with all perpendicular distances or distances of the endpoints.
Start or End can also be single points.
    '''
    if np.size(Startarray, axis = 0) ==1:
        Starttemp = np.repeat(Startarray, np.size(Endarray, axis = 0), axis = 0)
    else:
        Starttemp = Startarray
        
    if np.size(Endarray, axis = 0) ==1:
        Endtemp = np.repeat(Endarray, np.size(Startarray, axis = 0), axis = 0)
    else:
        Endtemp = Endarray
        
    
    #reshape the arrays and the points, have a Points*Start array
    oneaxis = np.size(Starttemp, axis = 0)
    twoaxis = np.size(Points, axis = 0)

    Starttemp = np.repeat(Starttemp, twoaxis, axis = 0)
    Endtemp = np.repeat(Endtemp, twoaxis, axis = 0)
    Points = np.tile(Points, (oneaxis,1))

    StartPunkteAbst = abstandarrays(Starttemp, Points)
    StartPunkteAbst = np.reshape(StartPunkteAbst, (oneaxis, twoaxis))
    
    EndPunkteAbst = abstandarrays(Endtemp, Points)
    EndPunkteAbst = np.reshape(EndPunkteAbst, (oneaxis, twoaxis))
    
    AngleAtStart = angle_between_connections_array(Points, Starttemp, Endtemp)
    AngleAtStart = np.reshape(AngleAtStart, (oneaxis, twoaxis))
    
    AngleAtEnd = angle_between_connections_array(Points, Endtemp, Starttemp)
    AngleAtEnd = np.reshape(AngleAtEnd, (oneaxis, twoaxis))
    
    
    
    #die Punkte mit über 90° nehmen einfach den Abstand vom Ende, die kleiner als 90° den senkrechten Abstand
    StartBiggerNinetyBool = (AngleAtStart >  np.pi/2)
    EndBiggerNinetyBool = (AngleAtEnd > np.pi/2)
    pointonconnectionbool = (AngleAtStart == 0) & (AngleAtEnd == 0)
    NotUseBool = np.invert(StartBiggerNinetyBool | EndBiggerNinetyBool | pointonconnectionbool)
    DistanceFromConnection = np.empty((oneaxis, twoaxis))
    DistanceFromConnection[NotUseBool] = np.sin(AngleAtStart[NotUseBool]) * StartPunkteAbst[NotUseBool]
    DistanceFromConnection[EndBiggerNinetyBool] = EndPunkteAbst[EndBiggerNinetyBool]
    DistanceFromConnection[StartBiggerNinetyBool] = StartPunkteAbst[StartBiggerNinetyBool]
    DistanceFromConnection[pointonconnectionbool] = 0.
    return DistanceFromConnection, oneaxis, twoaxis


# EDIT: moved functions punktbeigerade and test_accessible_angles out of main function

# Ob eine Region außen ist. Dafür werden von dem Punkt Strahlen in alle Richtungen in 5° Schritten gemacht und diese dann in eine Liste geschrieben, welche Winkel frei sind.


def punktebeigerade(minabstand, pkte, gerade, aufpunkt, laenge):
    '''
aufpunkt, der Punkt von wo aus geht
gerade: normiert
gibt True zurück, wenn kein Punkt in der Nähe der Geraden ist.
    '''
    kantenlaenge = 4 * minabstand
    wuerfeldiaghalbe = np.sqrt(3)/2 * kantenlaenge
    
    anzahlwuerfel = int(laenge / wuerfeldiaghalbe) + 1 
    
    #nun die Verbindungsgerade zwischen den beiden Punkten. v = m * t + x0 mit normiertem m und t (Abstand*parameter)
    wuerfelmitten = []

    for i in range(0, anzahlwuerfel):
        wuerfelmitten.append( gerade * (wuerfeldiaghalbe * (i + 1)) + aufpunkt)
    
        
    wuerfelmitten = np.array(wuerfelmitten)
        

    
    
    #minimale Abstand, den etwas haben muss, von Würfelmittelpunkt, ab dem wir sagen, dass was zu nah ist
    minabstandcalc = np.sqrt(5) * minabstand
    
    
    #das Einschränken der Werte auf die Würfelinnereien
    for mitte in wuerfelmitten:
        keep = ((pkte[:,0] > (mitte[0] - (kantenlaenge / 2))) & (pkte[:,0] < (mitte[0] + (kantenlaenge / 2))) & 
               (pkte[:,1] > (mitte[1] - (kantenlaenge / 2))) & (pkte[:,1] < (mitte[1] + (kantenlaenge / 2))) & 
               (pkte[:,2] > (mitte[2] - (kantenlaenge / 2))) & (pkte[:,2] < (mitte[2] + (kantenlaenge / 2))))   
        
        
        wuerfelpunkte = pkte[keep]
        if np.size(wuerfelpunkte) == 0:
            continue
        
        mintemp = np.min(abstandpktzuarray(mitte, wuerfelpunkte))
        
        if  mintemp < minabstandcalc:
            return False
            break
         
    else:
        return True
    

def test_accessible_angles(winkelarray, length, anfangspunkt, proteinpoints, gerade = np.array([0,0,1])):
    '''
    angles are measured from z-axis, returns a boolean array to slice with.
    '''
    moeglichewinkelanfangbool = []

    for winkel in winkelarray:
        moeglichewinkelanfangbool.append(punktebeigerade(minabstand, PointsOfAllSubunits, drehenxy(winkel[0], winkel[1], gerade),                                                         anfangspunkt , maxvonanfang))

    return np.array(moeglichewinkelanfangbool)
    


#displacement ist wirklich die Verschiebung im 3d raum, deshalb müssen die Längen dreimal draufgemacht werden.
def make_displacements(lengtharray, displacementarray):
    oneaxis = np.size(lengtharray)
    twoaxis = np.size(displacementarray, axis = 0)
    
    disptiled = np.tile(displacementarray, (oneaxis, 1))
    lengthshaped = np.repeat(lengtharray, 3 * twoaxis)
    lengthshaped = np.reshape(lengthshaped, (oneaxis * twoaxis, 3))
    
    return disptiled * lengthshaped
    
    

def sort_out_by_protein(startingarray, endingarray, proteinpoints, mindist, beforearray = None):
    '''
    startingarray must be an array of (x,3) shape. so add it as: [startingarray]
    beforearray is used, if also arrays before the connection need to be sliced. Then the boolarray is returned.
    '''
    if np.size(startingarray, axis=0) == 1:
        starttemp = np.repeat(startingarray, np.size(endingarray, axis=0), axis =0)
    else:
        starttemp = startingarray
    oneaxis = np.size(endingarray, axis = 0)    
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
    connectpointbool = ((startprotlength < startendlength) & (endprotlength < startendlength) & ((startprotlength + endprotlength) < (np.sqrt(np.square(startendlength)+mindist**2)+mindist)))
    connectpointbool = np.invert(connectpointbool.any(axis = 1) )  
    
    
    if beforearray == None:    
        if np.size(startingarray, axis=0) == 1:
            return [np.float16(startingarray), np.float16(endingarray[connectpointbool])]
        else:
            return [np.float16(startingarray[connectpointbool]), np.float16(endingarray[connectpointbool])]
    else:
        return (np.float16(beforearray[connectpointbool]), np.float16(startingarray[connectpointbool]), np.float16(endingarray[connectpointbool]))


# Wir fangen sowohl vorne als auch hinten an, mit allen Winkeln, die möglich sind und allen Längen, die möglich sind. Wir bekommen dann Arrays von den ersten Punkten und den letzten Punkten nach dem Protein.

def naechstepunkte(anfangsarray, verschiebungsarray):
    '''
    gibt ein Array zurück, das zu jedem Punkt, jede Verschiebung macht aus dem verschiebungsarray. Verschiebungsarray
    sind einfach Vektoren, wie das verschoben werden kann
    anfangsarray sind Vektoren, von denen wir ausgehen.
    '''
    laengeanfang = np.size(anfangsarray, axis=0)
    laengeversch = np.size(verschiebungsarray, axis=0)
    hilfanfang = np.float16(np.repeat(anfangsarray, laengeversch, axis=0))
    hilfversch = np.float16(np.tile(verschiebungsarray, (laengeanfang, 1)))
    return [hilfanfang, hilfanfang + hilfversch]

def aussortierennachpunken(punktearray, proteinpunkte, minabstand, maxabstand):
    '''
    schmeißt Punkte raus, die in dem Protein liegen, bzw. die zu weit vom Protein weg sind
    gibt ein Bool Array raus, mit dem man das Punktearray slicen kann, vom Protein wird nur jeder 4 Punkt verwendet
    '''
    
    temp1 = np.repeat(punktearray, np.size(proteinpunkte[::4], axis=0), axis =0)
    temp2 = np.tile(proteinpunkte[::4], (np.size(punktearray, axis=0),1))
    abstaende = np.reshape(abstandarrays_quadr(temp1, temp2), (np.size(punktearray, axis=0), np.size(proteinpunkte[::4], axis=0)))
    minimaleabst = np.min(abstaende, axis=1)
    keep = (minimaleabst < maxabstand**2) & (minimaleabst > minabstand**2)
    return keep
    


def gaussian_normed(x, sig, mu):
    return 1/(sig*np.sqrt(2*np.pi)) * np.exp(-0.5 * ((x-float(mu))/sig) ** 2)

#in anglearray there are always the actual angles in it
#IMPORTANT: here should never be a 0 in it
def angle_weighing(anglearray, angletosequence = angletosequence):
    #build function
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
    functionvalues = np.zeros(np.size(MiddleArray, axis = 0))
    functionvalues[tocalculate] = angle_weighing(angles)
    return functionvalues

#needs a on one normed array of the weighing of the points, if not all points are equally weighed

#TODO: Start can be array or just points, End has to be an array...
def unpreferable_places(Start, End, ProteinPoints, AminoacidNumberArray, ToBeWeighedAAInput, WeighingofAA, substratelist):
    if np.size(Start, axis = 0) ==1:
        Start = np.repeat(Start, np.size(End, axis = 0), axis = 0)
        
    if np.size(End, axis = 0) ==1:
        End = np.repeat(End, np.size(Start, axis = 0), axis = 0)
    
    #all the normal aminoacids from the arrays
    SliceToBeWeighed = np.in1d(ToBeWeighedAAInput, AminoacidNumberArray)
    ToBeWeighedAA = ToBeWeighedAAInput[SliceToBeWeighed]
    
    #reduce the points to their mean, so that every aminoacid is equally weighed and not long ones are more important than
    #than short ones
    Points = []
    for number in ToBeWeighedAA:
        Points.append(np.mean(ProteinPoints[AminoacidNumberArray == number], axis = 0))
    Points = np.array(Points)
    
    toappendtoweighingofAA = np.array([])
    #for the substrate
    for sublist in substratelist:
        if sublist[0] in AminoacidNumberArray:
            activepoint = np.mean(ProteinPoints[AminoacidNumberArray == sublist[0]], axis = 0)
            boolangles = test_accessible_angles(winkelarray, sublist[1], activepoint, ProteinPoints)
            lengtharray = np.array([0.2, 0.3, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7, 0.8, 1.]) * sublist[2]
            hereangles = winkelarray[boolangles]
            
            dispnorm = [np.array([0,0,0])]
            for winkel in hereangles:
                temp = drehenxy(winkel[0], winkel[1], np.array([0,0,1]))
                np.append(dispnorm, [temp], axis = 0)
                
            disps = make_displacements(lengtharray, dispnorm)
            disps = disps[(disps != np.array([0,0,0])).any(axis = 1)]
            #also add the activesite
            if np.size(Points) == 0:
                Points = np.concatenate((disps + activepoint, [activepoint]), axis = 0)
            else:
                Points = np.concatenate((Points, disps + activepoint, [activepoint]), axis = 0)
            toappendtoweighingofAA = np.append(toappendtoweighingofAA, np.ones(np.size(disps, axis = 0) + 1) /
                      (np.size(disps, axis = 0) + 1) * sublist[1])
            
    
    calc = (Start != End).any(axis = 1)
    Starttemp = Start[calc]
    Endtemp = End[calc]
    
    DistanceFromConnection, oneaxis, twoaxis = distance_from_connection(Starttemp, Endtemp, Points)
   
    
    if WeighingofAA == None:
        WeighingofAA = np.ones(twoaxis)

        
    #the array is normalized here and gets the size of the points, there can be set in arbitrary numnbers for the weighing
    WeighingofAAtemp = WeighingofAA[SliceToBeWeighed]
    WeighingofAAtemp = np.concatenate((WeighingofAAtemp, toappendtoweighingofAA))
    WeighingofAAtemp = (WeighingofAAtemp/np.mean(WeighingofAAtemp))
    WeighingofAAtemp = np.tile(WeighingofAAtemp, (oneaxis,1))
    WeighingofAAtemp = np.reshape(WeighingofAAtemp, (oneaxis, twoaxis))
      
        
    #TODO: zu welcher Potenz soll das dann gehen?
    ValueOfPoint = WeighingofAAtemp / (DistanceFromConnection ** 2)
    
    returns = np.zeros(np.size(Start, axis = 0))
    returns[calc] = np.sum(ValueOfPoint, axis = 1)
    return returns


def distance_from_surface(beforearray, testarray, ProteinPoints, Afterpoint = None):
    '''
    calculates the distances of the testarrays points from the surface as just the minimum of the distances to all protein 
    points. It doesn't calculate the points that are equal to the points of the beforearray, so that these are not taken double.
    And it checks that the points don't lie on the endpoint.
    Returns the distance divided by the minimal distance for norming the values somehow.
    '''
    Horiz_Axis = np.size(ProteinPoints, axis = 0)
    testsize = np.size(testarray, axis = 0)
    
    
    if np.size(beforearray, axis = 0) == 1:
        beforearray = np.repeat(beforearray, testsize, axis = 0)        
        
    calc = (beforearray != testarray).any(axis = 1)
    if Afterpoint != None:
        Afterpoint = np.repeat(Afterpoint, testsize, axis = 0)
        calc = (Afterpoint != testarray).any(axis = 1) & calc
    
    FirstPoints = testarray[calc]
    
    Vert_Axis = np.size(FirstPoints, axis = 0)
    Prottemp = np.tile(ProteinPoints, (Vert_Axis, 1))
    if Vert_Axis == 0:
        Distancesret = np.zeros(testsize)
    else:
        Firsttemp = np.repeat(FirstPoints, Horiz_Axis, axis = 0)
        Distances = abstandarrays(Firsttemp, Prottemp)    
        Distances = np.reshape(Distances, (Vert_Axis, Horiz_Axis))
        Distances = np.min(Distances, axis = 1)
        Distancesret = np.zeros(testsize)
        #TODO: Über Potenz nachdenken
        Distancesret[calc] = (Distances - minabstand) ** 2 / minabstand
    
    return Distancesret


def weighing_function_rigids(StartPoint, FirstArray, SecondArray, ThirdArray, EndPoint, ProteinPoints, AminoacidNumberArray, ToBeWeighedAA, WeighingofAA = None, substratelist = None):
    
    LinkerLength = abstandpktzuarray(StartPoint, FirstArray) + abstandarrays(FirstArray, SecondArray)     + abstandarrays(SecondArray, ThirdArray) + abstandpktzuarray(EndPoint, ThirdArray) 
    
    LengthNormed = LinkerLength / (abstand(StartPoint, EndPoint))
    
    #catch where there are no new points in the SecondArray
    SecondAngles = angle_function(FirstArray, SecondArray, ThirdArray)
    SecondAngles[SecondAngles == 0] = angle_function(StartPoint, SecondArray[SecondAngles == 0], ThirdArray[SecondAngles == 0])
    
    Angles = angle_function(StartPoint, FirstArray, SecondArray) + SecondAngles +     angle_function(SecondArray, ThirdArray, EndPoint)
    
    if ToBeWeighedAA == None:
        SiteInfluenceNormed = np.zeros(np.size(Angles))
    else:
        SiteInfluenceNormed = unpreferable_places([StartPoint], FirstArray, ProteinPoints, AminoacidNumberArray, ToBeWeighedAA,
                                                  WeighingofAA, substratelist) + \
        unpreferable_places(FirstArray, SecondArray, ProteinPoints, AminoacidNumberArray, ToBeWeighedAA,
                            WeighingofAA, substratelist) + \
        unpreferable_places(SecondArray, ThirdArray, ProteinPoints, AminoacidNumberArray, ToBeWeighedAA,
                            WeighingofAA, substratelist) + \
        unpreferable_places([EndPoint], ThirdArray, ProteinPoints, AminoacidNumberArray, ToBeWeighedAA,
                            WeighingofAA, substratelist)
    
    DistancesFromProtein = (distance_from_surface([StartPoint], FirstArray, ProteinPoints) + 
                            distance_from_surface(FirstArray, SecondArray, ProteinPoints) +
                            distance_from_surface(SecondArray, ThirdArray, ProteinPoints, [EndPoint]))
    
    weighedvalue = LengthNormed
    
    return (weighedvalue, LengthNormed * abstand(StartPoint, EndPoint), Angles,
            SiteInfluenceNormed, DistancesFromProtein)


def weighing_function_flex(StartPoint, FirstArray, SecondArray, ThirdArray, EndPoint, ProteinPoints, AminoacidNumberArray, ToBeWeighedAA, WeighingofAA = None, substratelist = None):
    
    LinkerLength = abstandpktzuarray(StartPoint, FirstArray) + abstandarrays(FirstArray, SecondArray)     + abstandarrays(SecondArray, ThirdArray) + abstandpktzuarray(EndPoint, ThirdArray) 
    
    LengthNormed = LinkerLength / (abstand(StartPoint, EndPoint))
    
    Angles = angle_function(FirstArray, SecondArray, ThirdArray)
    
    if ToBeWeighedAA == None:
        SiteInfluenceNormed = np.zeros(np.size(Angles))
    else:
        SiteInfluenceNormed = unpreferable_places(FirstArray, SecondArray, ProteinPoints, AminoacidNumberArray,
                                                  ToBeWeighedAA, WeighingofAA, substratelist) + \
        unpreferable_places(SecondArray, ThirdArray, ProteinPoints, AminoacidNumberArray, ToBeWeighedAA, 
                            WeighingofAA, substratelist) 
    
    DistancesFromProtein = distance_from_surface(FirstArray, SecondArray, ProteinPoints) 
    
    weighedvalue = LengthNormed
    
    return (weighedvalue, LengthNormed * abstand(StartPoint, EndPoint), Angles,
            SiteInfluenceNormed, DistancesFromProtein)
#Aus dem Weighingstring nutzbare Form machen.


def make_weighingarrays(Userstring):
    
    """
Userstring ist von der Form: 273,10 280-290,5 298,7,35.6  usw. (Leerzeichen trennen Einträge, , for single residues
- for ranges, second, for the diameter of the substrate)
If nothing should be weighted, insert ""
    
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



def sort_out_by_angle (startingarray, middlearray, endingarray, angletosequence):
    '''
    returns a boolian array which paths to keep, middle and endingarray must have same dimension, startingarray is only one 
    entry
    '''
    if np.size(startingarray, axis = 0) == 1:
        startingexp = np.repeat(startingarray, np.size(middlearray, axis=0), axis =0)
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
        tempmid = middlearray[tocalculate]
        tempend = endingarray[tocalculate]
        tocalctemp = tocalculate == False
        tempmid = np.concatenate((tempmid[keep], middlearray[tocalctemp]), axis = 0)
        tempend = np.concatenate((tempend[keep], endingarray[tocalctemp]), axis = 0)
        
        if np.size(startingarray, axis = 0) == 1: 
            return (tempmid, tempend)
        else:
            tempstart = np.concatenate((tempstart[keep], startingarray[tocalctemp]), axis = 0)
            return tempstart, tempmid, tempend
    else:
        if np.size(startingarray, axis = 0) == 1:
            return middlearray, endingarray
        else:
            return startingarray, middlearray, endingarray



def make_small_generator(PointArray, repetition, RAM, ProteinArray = None):
    '''
    RAM in GByte,
    repetition, how often is the largest array repeated
    '''
    AvailableRAM = float(RAM) * 1073741824 #in BytesWaBytesWarning
    
    
    try:
        PointSize = PointArray.nbytes    
    except:
        PointSize = PointArray * 2 #assumes, that it is the size of the array, and this is float 16
    
    if ProteinArray != None:
        proteinsize = np.size(ProteinArray, axis = 0)
    else:
        proteinsize = 1
        
    UsedMem = PointSize * proteinsize * repetition
    
    return int(UsedMem / AvailableRAM) + 1


def sort_out_by_distance(startingpoints, endingpoints, firstpoints, distance, variation):
    '''
    returns three arrays with all possible paths, made out of all possible combinations startingpoints to endingpoints
    that are in a certain distance
    '''
    
    starttemp = np.float16(np.repeat(startingpoints, np.size(endingpoints, axis=0), axis =0))
    endtemp = np.float16(np.tile(endingpoints, (np.size(startingpoints, axis=0),1)))
    abstaende = abstandarrays_quadr(starttemp, endtemp)
    keep = ((abstaende > (distance-variation)**2) & (abstaende < (distance+variation)**2))
    firsttemp = np.float16(np.repeat(firstpoints, np.size(endingpoints, axis=0), axis =0))
    return [firsttemp[keep], starttemp[keep], endtemp[keep]]


def sort_out_by_length (comefrompoints, gotopoints, linkerlaengen):
    '''
    returns a boolean array, with which you can slice the points, True means the values are kept
    comefrompoints can be either an x * 3 array or just a three array, then it is elongated
    '''
    
    if np.size(comefrompoints) == 3:
        comefrompoints = np.repeat([comefrompoints], np.size(gotopoints, axis = 0), axis = 0)
    else:
        if np.size(gotopoints) == 3:
            gotopoints = np.repeat([gotopoints], np.size(comefrompoints, axis = 0), axis = 0)
    
    arraylengthtemp = np.size(comefrompoints, axis = 0)
    lonetemp = abstandarrays(comefrompoints, gotopoints)
    #True means keep
    sortouttemp = np.bool8(np.zeros(arraylengthtemp))
    
    for LAENGE in linkerlaengen:
        sortouttemp = sortouttemp | ((lonetemp < (LAENGE + LENGTHACCURACYKO)) & (lonetemp > (LAENGE - LENGTHACCURACYKO)))
        
    return sortouttemp


##### Gestartet am 9.8. um 15:15 Uhr, 15:55 Uhr bei den Dreieckigen Linkern Versuch eines kompletten Durchlaufs, dann dreistunden für die dreieckigen Linker  Linkerohneeckeflex: 11000 erzeugt, bereits erstmal aussortiert. Linkermiteckeflex:  insgesamt 35000 flexible (also 24000 hinzugekommen)  erstepunkte 2200 erzeugt,  drittepunkte werden 850 000 erzeugt

def length_to_sequence(lengtharray, linkerdatenbank, linkerlaengen):
    #prepare for adding strings always
    addsequencearray = np.zeros(np.size(lengtharray), dtype=str)
    addsequencearray = np.array(addsequencearray, dtype=np.object)
    
    for i in range(len(linkerlaengen)):
        setseqbool = ((lengtharray >= linkerlaengen[i] - LENGTHACCURACYKO) &
                      (lengtharray <= (linkerlaengen[i] + LENGTHACCURACYKO)))
        addsequencearray[setseqbool] = addsequencearray[setseqbool] + linkerdatenbank[i]
        
    temp = (addsequencearray == "") & (lengtharray != 0.)
    addsequencearray[temp] = addsequencearray[temp] + "XXX" #TODO nur zum Testen, das muss noch raus!
    
    return addsequencearray

def angle_to_sequence(anglearray, angletosequence, angleseparators):
    addsequencearray = np.zeros(np.size(anglearray), dtype=str)
    addsequencearray = np.array(addsequencearray, dtype=np.object)
    
    for i in range(len(angletosequence)):
        setseqbool = (anglearray > angleseparators[i]) & (anglearray < angleseparators[i + 1])
        addsequencearray[setseqbool] = addsequencearray[setseqbool] + angletosequence[i][2]
    return addsequencearray

#returns the weightingarrays and the sequencearrays, concatenated
def translate_paths_to_sequences(startpoint, firstflex, secondflex, thirdflex, firstrig, secondrig, thirdrig,
                                 endpoint, linkerdatenbank, linkerlaengenKO, angletosequence, angleseparators,
                                 weightflex, weightrig):
    
    if weightflex != None:
        #flexible linkers
        sequenceflex = np.zeros(np.size(firstflex, axis = 0), dtype=str)
        sequenceflex = np.array(sequenceflex, dtype=np.object)
        sequenceflex = sequenceflex + ScarsAtStartseq

        withoutanglebool = (firstpointsflexible == secondpointsflexible).all(axis = 1)

        sequenceflex[withoutanglebool] = sequenceflex[withoutanglebool] +         length_to_sequence(abstandarrays(secondflex[withoutanglebool], thirdflex[withoutanglebool]), 
                           linkerdatenbank, linkerlaengenKO - (2 * LENGTHOFANGLEKO))


        withanglebool = np.invert(withoutanglebool)

        sequenceflex[withanglebool] = sequenceflex[withanglebool] +         length_to_sequence(abstandarrays(firstflex[withanglebool], secondflex[withanglebool]),
                           linkerdatenbank, linkerlaengenKO - LENGTHOFANGLEKO)

        sequenceflex[withanglebool] = sequenceflex[withanglebool] +         angle_to_sequence(angle_between_connections_array(firstflex[withanglebool], secondflex[withanglebool], 
                                                          thirdflex[withanglebool]), angletosequence, angleseparators)

        sequenceflex[withanglebool] = sequenceflex[withanglebool] +         length_to_sequence(abstandarrays(secondflex[withanglebool], thirdflex[withanglebool]), linkerdatenbank, 
                           linkerlaengenKO - LENGTHOFANGLEKO)
    
    if weightrig != None:
        #rigid linkers
        sequencerig = np.zeros(np.size(firstrig, axis = 0), dtype=str)
        sequencerig = np.array(sequencerig, dtype=np.object)
        sequencerig = sequencerig + ScarsAtStartseq


        sequencerig = sequencerig + length_to_sequence(abstandpktzuarray(startpoint, firstrig) -
                                                       FLEXIBLEATSTARTKO + LENGTHOFANGLEKO,  linkerdatenbank, linkerlaengenKO)
        sequencerig = sequencerig + angle_to_sequence(angle_between_connections_array([startpoint], firstrig, secondrig), 
                                                      angletosequence, angleseparators)

        sequencerig = sequencerig + length_to_sequence(abstandarrays(firstrig, secondrig), linkerdatenbank, linkerlaengenKO)
        sequencerig = sequencerig + angle_to_sequence(angle_between_connections_array(firstrig, secondrig, thirdrig), 
                                                      angletosequence, angleseparators)

        sequencerig = sequencerig + length_to_sequence(abstandarrays(secondrig, thirdrig), linkerdatenbank, linkerlaengenKO)
        sequencerig = sequencerig + angle_to_sequence(angle_between_connections_array(secondrig, thirdrig, [endpoint]), 
                                                      angletosequence, angleseparators)

        sequencerig = sequencerig + length_to_sequence(abstandpktzuarray(endpoint, thirdrig) -
                                                       FLEXIBLEATENDKO + LENGTHOFANGLEKO,  linkerdatenbank, linkerlaengenKO)
    

    if weightrig != None:
        if weightflex != None:
            sequence = np.concatenate((sequenceflex, sequencerig))
            retweight = np.concatenate((weightflex, weightrig), axis = 1)
            sequence = sequence + ScarsAtEndseq
            return sequence , retweight,    np.concatenate((firstflex, firstrig), axis = 0), np.concatenate((secondflex, secondrig), axis = 0),    np.concatenate((thirdflex, thirdrig), axis = 0)
        else:
            sequence = sequencerig
            retweight = weightrig
            sequence = sequence + ScarsAtEndseq
            return sequence , retweight, firstrig, secondrig, thirdrig
    elif weightflex != None:
        sequence = sequenceflex
        retweight = weightflex
        sequence = sequence + ScarsAtEndseq
        return sequence , retweight, firstflex, secondflex, thirdflex
    else:
        #replace sys.exit with own function
        loader.exit("There were absolutely no linkers found, that could be translated to sequences")








#thirdpoints are to be shifted and given back
def shift_points_to_linkerpatterns(secondpoints, thirdpoints, linkerlaengenKO):
    '''
    shifts thirdpoints to the secondpoints or away from them, so that the distance between second and third fits into the
    patterns that are provided by linkerlaengenKO.
    secondpoints and thirdpoints must have same dimension.
    
    returns the new thirdpoints
    '''
    lthreetemp = abstandarrays(secondpoints, thirdpoints)
    for LAENGE in linkerlaengenKO:
        if LAENGE == linkerlaengenKO[0]:
            comparedtopattern = lthreetemp - LAENGE
        else:
            comparedtopatterntwo = lthreetemp - LAENGE
            fusionbool = np.abs(comparedtopattern) > np.abs(comparedtopatterntwo)
            comparedtopattern[fusionbool] = comparedtopatterntwo[fusionbool]
    
    toberefinedbool = (np.abs(comparedtopattern) > LENGTHACCURACYKO)
    
    if toberefinedbool.any():
        toberefinedlengths = comparedtopattern[toberefinedbool]
        arraylengthtemp = np.size(toberefinedlengths)
        shifts = np.zeros(arraylengthtemp)
        #we calculate the shifts, to be sure we shift a bit farther than we need in the end.
        shifts[toberefinedlengths > 0] = -1 * (toberefinedlengths[toberefinedlengths > 0] - 
                                               LENGTHACCURACYKO + LENGTHACCURACYKO / 10.)
        shifts[toberefinedlengths < 0] = -1 * (toberefinedlengths[toberefinedlengths < 0] + 
                                               LENGTHACCURACYKO - LENGTHACCURACYKO / 10.)
        shifts = np.reshape(np.repeat(shifts, 3), (arraylengthtemp,3))
        lengthestemp = abstandarrays(thirdpoints[toberefinedbool] , secondpoints[toberefinedbool])
        lengthestemp = np.reshape(np.repeat(lengthestemp, 3), (arraylengthtemp,3))
        thirdpoints[toberefinedbool] = (((thirdpoints[toberefinedbool] - secondpoints[toberefinedbool]) /
                                        lengthestemp) * shifts ) + thirdpoints[toberefinedbool]

    return thirdpoints
    
    
    
    
    
def make_better_paths_rigid(startpoint, firstpoints, secondpoints, thirdpoints, endpoint):
    linkerlaengenKOtemp = np.append(linkerlaengenKO, 0.)
    lonetemp = abstandpktzuarray(startpoint, firstpoints)
    
    arraylengthtemp = np.size(lonetemp)
    #True bleibt
    
    keep = sort_out_by_length(startpoint, firstpoints, linkerlaengenKO + FLEXIBLEATSTARTKO - LENGTHOFANGLEKO)
    firstpoints = firstpoints[keep]
    secondpoints = secondpoints[keep]
    thirdpoints = thirdpoints[keep]
        
    thirdpoints = shift_points_to_linkerpatterns(secondpoints, thirdpoints, linkerlaengenKOtemp)
    
    keep = sort_out_by_length(thirdpoints, endpoint, linkerlaengenKO + FLEXIBLEATENDKO - LENGTHOFANGLEKO)
    firstpoints = firstpoints[keep]
    secondpoints = secondpoints[keep]
    thirdpoints = thirdpoints[keep]    
    
    return firstpoints, secondpoints, thirdpoints
    
    
def make_better_paths_flex(firstpoints, secondpoints, thirdpoints, endpoint):
    linkerlaengenKOtemp = np.append(linkerlaengenKO, 2*LENGTHOFANGLEKO)
    
    noanglebool = (firstpoints == secondpoints).all(1)
    thirdpoints[noanglebool] = shift_points_to_linkerpatterns(secondpoints[noanglebool],
                                                              thirdpoints[noanglebool], linkerlaengenKOtemp - 
                                                              2 * LENGTHOFANGLEKO)
    
    #keep Trues
    arraylengthtemp = np.size(noanglebool)
    sortouttemp = np.bool8(np.ones(arraylengthtemp))
    sortouttemp[noanglebool] = (abstandpktzuarray(endpoint, thirdpoints[noanglebool]) < FLEXIBLEATENDKO)
        
    return firstpoints[sortouttemp], secondpoints[sortouttemp], thirdpoints[sortouttemp]



#read the instructions file
#EDIT: put everything into a function named calc

def calc(instructionsfile, pdbfile, resultfile ):
    # EDIT: removed file references and replaced with parameter
    f = open(instructionsfile, "r")

    line = f.readline()
    line = line.strip()
    #EDIT: removed pdbname
    subunitforwork, projectname, functionnumber, angleforworkstart, angleforworkend, natext, RAMofclient = line.split("," )

    RAMofclient = float(RAMofclient)    

    f.close()

    #make a directory for the files if not exists yet

    if (not os.path.exists("files")):
        os.makedirs("files")
    #PDB geht von N zu C Terminus     
        

    UserDefinedProjectName = projectname #for saving of the files, für DNMT1daten einfach "" machen

    f = open(pdbname, 'r')



    wholex = []
    wholey = []
    wholez = []
    wholeatom = []
    wholeaminos = []
    wholesubunit = []
    wholeasnr = []


    #line.split kann nicht verwendet werden, weil manchmal die spalten ineinander verschmelzen, weil das Format doof ist.

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
            
    f.close()

    #aus allen Listen arrays machen
    wholeatom = np.array(wholeatom)
    wholeaminos = np.array(wholeaminos)
    wholesubunit = np.array(wholesubunit)
    wholeasnr = np.array(wholeasnr)
    #731-1602 dnmt1
    #oder 650 - 1602

    differentsubunits = np.unique(wholesubunit)

    #get parts, that aren't wanted out of the PDB files

    #TODO hierüber nachdennken!!! was die Regionen sind, die gewählt werden

    UserChosenIgnoreRegions = None #default is none, being a LIST of tuples of (21, 832, 'A'), with subunit, and then interval including the ends
    IgnoreSubUnit = differentsubunits[differentsubunits != subunitforwork] #is a tupel with to be ignored subunits
    IgnoreIndices = np.bool8(np.ones(np.size(wholeasnr)))

    #Ignoreindices True means the value is kept
    if IgnoreSubUnit != None:
        for SubUnit in IgnoreSubUnit:
            IgnoreIndices = IgnoreIndices & (wholesubunit != SubUnit)


    if UserChosenIgnoreRegions != None:
        for RegionOnSubunit in UserChosenIgnoreRegions:
            IgnoreIndices = IgnoreIndices & np.invert((wholeasnr < RegionOnSubunit[1]) & (wholeasnr > RegionOnSubunit[0]) &   (wholesubunit == RegionOnSubunit[2]))

    wholeatom = wholeatom[IgnoreIndices]
    wholeaminos = wholeaminos[IgnoreIndices]
    wholesubunit = wholesubunit[IgnoreIndices]
    wholeasnr = wholeasnr[IgnoreIndices]


    wholex = np.float16(np.array(wholex))        
    wholey = np.float16(np.array(wholey))
    wholez = np.float16(np.array(wholez))
    #that should be sliced out of the PDB
    wholex = wholex[IgnoreIndices]
    wholey = wholey[IgnoreIndices]
    wholez = wholez[IgnoreIndices]

    anzahl = len(wholex)


    #let the user choose, what part should be circularized interests him.
    SubUnitChosen = subunitforwork
    UserChosenStart = None
    UserChosenEnd = None

    if UserChosenEnd == None:
        UserChosenEnd =  np.max(wholeasnr[wholesubunit == SubUnitChosen])
        
    if UserChosenStart == None:
        UserChosenStart = np.min(wholeasnr[wholesubunit == SubUnitChosen])

    #non helical regions are called scars
    ScarsAtStartseq = "GG"
    ScarsAtStart = len(ScarsAtStartseq)
    ScarsAtEndseq = natext   #TODO richtige Sequenz!
    ScarsAtEnd = len(ScarsAtEndseq)


    MissingAtStart = np.min(wholeasnr[wholesubunit == SubUnitChosen]) - UserChosenStart
    MissingAtEnd = UserChosenEnd - np.max(wholeasnr[wholesubunit == SubUnitChosen]) 

    PartToCircularizeBool = (((wholeasnr >= UserChosenStart) & (wholesubunit == SubUnitChosen)) & (wholeasnr <= UserChosenEnd)) #hier kann man einstellen, welche AS behalten werden sollen.

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

    #TODO Estimation of startingpoint, or user interface to get it.

    anfangspunkt = np.ravel(pkte[(InterestingAANr == InterestingAANr[0]) & (InterestingAtom == "N  ")])
    endpunkt = np.ravel(pkte[(InterestingAANr == InterestingAANr[-1]) & (InterestingAtom == "C  ")])


    AmountOfAtomsFirstAA = np.size(InterestingAANr[InterestingAANr == InterestingAANr[0]])  #anzahl an Atomen in der erstenas
    AmountOfAtomsLastAA = np.size(InterestingAANr[InterestingAANr == InterestingAANr[-1]])  #amount of atoms in last AS

    #evtlraus

    #pickle.dump((pkte, InterestingAminos, InterestingAtom, InterestingAANr), open("files/savepoints{projectname}.p".format(projectname = UserDefinedProjectName), "wb"))

    #TODO Winkel einfügen

    #this dictionary contains the medium, the standrad-deviation and the sequence of all the angles
    angletosequence = [(45., 25., "AASGAA"),(79., 29., "AALAA"), (84., 11., "AAWAA"), (85., 19., "ASNA"),
                       (100., 18., "ASA"), (120., 6., "AGA"), (145., 15., "VV"), ]
    angleseparators = [0.]

    #the separators are there where the amount of sigmas is the same from both directions
    for i in range(len(angletosequence)-1):
        factor = (angletosequence[i+1][0]-angletosequence[i][0])/(angletosequence[i+1][1]+ angletosequence[i][1])
        angleseparators.append(factor * angletosequence[i][1] + angletosequence[i][0])
    angleseparators.append(180.)



    #Längenkalibration, wir wissen, dass der Abstand von c-c 154 pm ist.
    #Wir machen das am Glycin, weil das am einfachsten für uns ist.
    try:
        eichnutz = ((wholeaminos == "GLY") & (wholeatom == "C  ") | ((wholeaminos == "GLY") & (wholeatom == "CA ")))
        xeich = wholex[eichnutz]
        yeich = wholey[eichnutz]
        zeich = wholez[eichnutz]


        #das sieht so komisch aus, wegen alter Version
        abstaendeeich= abstand( np.array([xeich[0::2],yeich[0::2],zeich[0::2]]),np.array([xeich[1::2],yeich[1::2],zeich[1::2]]))
        kalib = 154. / np.mean(abstaendeeich) #pm
        kalibfehl = np.std(abstaendeeich) * kalib

    except:
        kalib = 100.
        kalibfehl = 0.
        


    #globale Variablen:

    #Entfernung, die der Linker mindestens immer haben sollte geschaetzter Wert 5 Angström, eine Alpha Helix hat Radius 2.3A

    minabstand = 500/kalib #in pm

    #Entfernung, die ein Linker maximal haben darf vom Protein

    maxabstand = 5000/kalib

    LengthOfFlexibleAA = 250 / kalib #between 250 and 350
    FLEXIBLEATSTARTKO = (MissingAtStart + ScarsAtStart) * LengthOfFlexibleAA
    FLEXIBLEATENDKO = (MissingAtEnd + ScarsAtEnd) * LengthOfFlexibleAA


    # Wir testen, ob sich die Enden einfach direkt verbinden lassen. Dafür schauen wir ob auf der Verbindungslinie zwischen den beiden Enden im senkrechten Abstand alle Punkte mindestens einen gewissen Abstand haben. Da aber der Punkteraum diskret ist und nicht ausgeschmiert, schauen wir einfach für jeden Würfel um die Verbindungslinie, welches der geringste Abstand eines Punktes ist. Ist dieser geringer als unser geforderter Mindestabstand, bricht der Algorithmus sofort ab und es kann weiter gehen. Die Würfel sind nur dazu da, dass wir nicht immer den Abstand des gesamten Proteins zur Linie berechnen müssen. Wenn ein Punkt zu nah ist, finden wir ihn so auf jeden Fall.
    # 
    # Wir müssen auf jeden Fall den Abstand zwischen zwei Messpunkten so wählen, dass selbst wenn der Punkt am ungünstigsten liegt, wir ihn aussortieren. Lieber zu früh aussortieren als zu spät und dann eben das normale Prozedere durchmachen lassen. Wir wählen die Abstände so, dass immer der nächste Punkt 
    # 
    # Der erste Messpunkt muss so sein, dass nicht unser Startpunkt in den ersten Würfel fällt, genauso beim letzten.

    # In[9]:

    abstandanfend = abstand(anfangspunkt, endpunkt)
    kantenlaenge = 4 * minabstand
    wuerfeldiaghalbe = np.sqrt(3)/2 * kantenlaenge


    anzahlwuerfel = int(abstandanfend / wuerfeldiaghalbe) #wir setzen einen mehr ein, als wir müssten
    if anzahlwuerfel == 0:
        if abstandanfend < (2* minabstand):
            loader.exit("The ends are too close")
        else:
            wuerfelmitten = np.array([(anfangspunkt-endpunkt)/2])
            kantenlaenge = abstandanfend / np.sqrt(3)
            wuerfelabstand = 0
    elif anzahlwuerfel == 1:
        kantenlaenge = abstandanfend / np.sqrt(3)
        wuerfeldiaghalbe = np.sqrt(3)/2 * kantenlaenge
        wuerfelmitten = (endpunkt-anfangspunkt)/abstandanfend * (wuerfeldiaghalbe) + anfangspunkt
        wuerfelabstand = 0
        
    else:
        wuerfelabstand = (abstandanfend - (2* wuerfeldiaghalbe))/(anzahlwuerfel - 1)

        #nun die Verbindungsgerade zwischen den beiden Punkten. v = m * t + 0 mit normiertem m und t (Abstand*parameter)
        wuerfelmitten = []
        for i in range(0, anzahlwuerfel):
            wuerfelmitten.append( (endpunkt-anfangspunkt)/abstandanfend * (wuerfelabstand * i + wuerfeldiaghalbe) + anfangspunkt)
            
        wuerfelmitten = np.array(wuerfelmitten)
        

    #minimale Abstand, den etwas haben muss, von Würfelmittelpunkt, ab dem wir sagen, dass was zu nah ist, das ist auch 
    #der Fehler den wir haben können.
    minabstandcalc = np.sqrt(minabstand**2 + wuerfelabstand**2)

    derallernaechstepunkt = None

    #das Einschränken der Werte auf die Würfelinnereien
    if np.size(wuerfelmitten) == 3:
        mitte = wuerfelmitten
        keep = ((PointsOfAllSubunits[:,0] > (mitte[0] - (kantenlaenge / 2))) & (PointsOfAllSubunits[:,0] < (mitte[0] + (kantenlaenge / 2))) &
                (PointsOfAllSubunits[:,1] > (mitte[1] - (kantenlaenge / 2))) & (PointsOfAllSubunits[:,1] < (mitte[1] + (kantenlaenge / 2))) & 
                (PointsOfAllSubunits[:,2] > (mitte[2] - (kantenlaenge / 2))) & (PointsOfAllSubunits[:,2] < (mitte[2] + (kantenlaenge / 2))))
                
        wuerfelpunkte = PointsOfAllSubunits[keep]

        mintemp = np.min(abstandpktzuarray(mitte, wuerfelpunkte))

        if  mintemp < minabstandcalc:
            temp = 0

        else:
            if derallernaechstepunkt == None:
                derallernaechstepunkt = mintemp
            elif mintemp < derallernaechstepunkt:
                derallernaechstepunkt = mintemp

            else:
                temp = 0
    else:

        for mitte in wuerfelmitten:
            keep = ((PointsOfAllSubunits[:,0] > (mitte[0] - (kantenlaenge / 2))) & (PointsOfAllSubunits[:,0] < (mitte[0] + (kantenlaenge / 2))) & (PointsOfAllSubunits[:,1] > (mitte[1] - (kantenlaenge / 2))) & (PointsOfAllSubunits[:,1] < (mitte[1] + (kantenlaenge / 2))) &                 (PointsOfAllSubunits[:,2] > (mitte[2] - (kantenlaenge / 2))) & (PointsOfAllSubunits[:,2] < (mitte[2] + (kantenlaenge / 2))))   

            wuerfelpunkte = PointsOfAllSubunits[keep]

            mintemp = np.min(abstandpktzuarray(mitte, wuerfelpunkte))

            if  mintemp < minabstandcalc:
                break

            else:
                if derallernaechstepunkt == None:
                    derallernaechstepunkt = mintemp
                elif mintemp < derallernaechstepunkt:
                    derallernaechstepunkt = mintemp

        else:
            temp = 0
        


    #das sind nun 2592 Berechnungen...
    testwinkel = np.mgrid[0:180:5, 0:360:5] * np.pi/180 #Endwinkel nicht enthalten, null mit drinnen, das sind ja auch nur 70 Rechn extra
    winkelarray = np.reshape(np.ravel(testwinkel), (2592,2), 'F')    



    #Ueberprüfen, ob der Anfang innen ist.
    maxvonanfang = np.max(abstandpktzuarray(pkte[0] ,PointsOfAllSubunits))
    #geradenarray = np.reshape(np.ravel(drehenxy(testwinkel[0], testwinkel[1], gerade), order = 'F'), (2592,3), 'C')

    moeglichewinkelanfangbool = test_accessible_angles(winkelarray, maxvonanfang, anfangspunkt, PointsOfAllSubunits)   


    #Überprüfen, ob das Ende innen ist.
    maxvonende = np.max(abstandpktzuarray(endpunkt ,PointsOfAllSubunits))


    moeglichewinkelendebool = test_accessible_angles(winkelarray, maxvonende, endpunkt, PointsOfAllSubunits)



    moeglichewinkelanfang = winkelarray[moeglichewinkelanfangbool]
    moeglichewinkelende = winkelarray[moeglichewinkelendebool]
    if (np.size(moeglichewinkelanfangbool) == 0) | (np.size(moeglichewinkelendebool) == 0):
       #TODO, vielleicht noch mit flexiblem Linker verbindbar? Einfach der Test, ob es an der Oberfläche ist.
       loader.exit("One end is covered in the protein, it is not circularizable")


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

    #TODO die Länge genau bestimmen
    LengthOfAngle = 450 #in pm
    LENGTHOFANGLEKO = LengthOfAngle / kalib
    #hier muss man eintragen, welche Helix-linkerlängen in AS möglich sind.
    linkerdatenbank = np.array(["AEAAAK", "AEAAAKA", "AEAAAKAA", "AEAAAKEAAAK", "AEAAAKEAAAKA", "AEAAAKEAAAKEAAAKA", "AEAAAKEAAAKEAAAKEAAAKA", "AEAAAKEAAAKEAAAKEAAAKEAAAKA"])
    linkerlaengenAS = []

    for i in range(len(linkerdatenbank)):
        linkerlaengenAS.append(len(linkerdatenbank[i]))
        
    linkerlaengenAS = np.array(linkerlaengenAS)
    linkerlaengenME = linkerlaengenAS * 150 + 2*LengthOfAngle #in pm
    linkerlaengenKO = linkerlaengenME / kalib #in koordinaten

    LENGTHACCURACY = 75
    LENGTHACCURACYKO = LENGTHACCURACY / kalib
    #TODO darüber nachdenken, ob 1 wirklich richtig ist.
    SortOutLinkers = linkerlaengenKO < 1*maxvonanfang

    linkerlaengenAS = linkerlaengenAS[SortOutLinkers]
    linkerlaengenME = linkerlaengenME[SortOutLinkers]
    linkerlaengenKO = linkerlaengenKO[SortOutLinkers]
    linkerdatenbank = linkerdatenbank[SortOutLinkers]

    laengstesstueck = np.max(linkerlaengenKO)
    anzahllinker = np.size(linkerlaengenKO)

    maxlinkerAS = int(3 * max(maxvonanfang, maxvonende)) #pi*0.75/1.5 in Aminosäuren
    maxlinkerKO = maxlinkerAS * 150/kalib
    anzahleckenmax = maxlinkerKO / np.max(linkerlaengenKO)
    anzahleckenmin = abstandanfend / np.min(linkerlaengenKO)





    #wie genau müssen sich die Stücke treffen wird durch hitgenauig bestimmt, es ist sin(5°) * maximale linkerlänge
    #+ einen Helixanteil
    #~500s
    hitgenauig = 0.0436 * laengstesstueck

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


    # We insert new possible linkers, these are either straight connections between the ends with flexible parts or with maximum one angle in the linker. The point is, that here the flexible ends are estimated better. 

    #without any edge, 
    #+1 because of range

    if (ScarsAtStart + MissingAtStart) > 3:
        FLEXATSTART = np.logspace(np.log10(1.5), np.log10(ScarsAtStart + MissingAtStart), num=4) * LengthOfFlexibleAA
    else:
        FLEXATSTART = np.append(np.arange(2, (ScarsAtStart + MissingAtStart+1)), 1.5 ) * LengthOfFlexibleAA
        
    if (ScarsAtEnd + MissingAtEnd) > 3:
        FLEXATEND = np.logspace(np.log10(1.5), np.log10(ScarsAtEnd + MissingAtEnd), num=4) * LengthOfFlexibleAA
    else:
        FLEXATEND = np.append(np.arange(2, (ScarsAtEnd + MissingAtEnd+1)), 1.5 ) * LengthOfFlexibleAA


    if functionnumber == "1":

        secondpointsflexible = firstpointsflexible = np.float16(make_displacements(FLEXATSTART, startdisp) + anfangspunkt)
        thirdpointsflexible = np.float16(make_displacements(FLEXATEND, enddisp) + endpunkt)

        amountofthirdpoints = np.size(thirdpointsflexible, axis = 0)
        amountofsecondpoints = np.size(secondpointsflexible, axis = 0)

        #reduce the amount of points in the protein, that should be checked, as a cylinder around start -> end
        heretousepoints = pkte[np.ravel(distance_from_connection([anfangspunkt], [endpunkt], pkte)[0] <                        (minabstand + np.max(np.concatenate((FLEXATSTART, FLEXATEND)))))]


        MakeSmall = make_small_generator(np.size(secondpointsflexible) * np.size(thirdpointsflexible),
                                         1.5 , RAMofclient , ProteinArray = heretousepoints)

        teiler = np.size(secondpointsflexible, axis=0)/(MakeSmall)

        for i in range(0,(MakeSmall)):

            temp1, temp2, temp3 = sort_out_by_distance(secondpointsflexible[i*teiler:(i+1)*teiler], thirdpointsflexible,
                                        firstpointsflexible[i*teiler:(i+1)*teiler], abstandanfend, 300 / kalib) 
            #300 ist etwa die Hälfte des Unterschieds zwischen zwei Linkerstücken
            
            keep = (distance_from_connection(temp2, temp3, heretousepoints)[0] >= minabstand).all(axis = 1)
            
            temp1 = temp2 = temp2[keep]
            temp3 = temp3[keep]
            
            if i == 0:
                firstpointsflexibletemp, secondpointsflexibletemp, thirdpointsflexibletemp = temp1, temp2, temp3
            else:
                firstpointsflexibletemp = np.concatenate((firstpointsflexibletemp, temp1), axis =0)
                secondpointsflexibletemp = np.concatenate((secondpointsflexibletemp, temp2), axis =0)
                thirdpointsflexibletemp = np.concatenate((thirdpointsflexibletemp, temp3), axis =0)

        if (i+1)*teiler < np.size(secondpointsflexible, axis=0):
            temp1, temp2, temp3 = sort_out_by_distance(secondpointsflexible[(i+1)*teiler:], thirdpointsflexible,
                                        firstpointsflexible[(i+1)*teiler:], abstandanfend, 300 / kalib)

            keep = (distance_from_connection(temp2, temp3, heretousepoints)[0] >= minabstand).all(axis = 1)

            temp1 = temp2 = temp2[keep]
            temp3 = temp3[keep]

            firstpointsflexible  = np.concatenate((firstpointsflexibletemp,  temp1), axis =0)
            secondpointsflexible = np.concatenate((secondpointsflexibletemp, temp2), axis =0)
            thirdpointsflexible  = np.concatenate((thirdpointsflexibletemp,  temp3), axis =0)
        else:
            firstpointsflexible  = firstpointsflexibletemp
            secondpointsflexible = secondpointsflexibletemp
            thirdpointsflexible  = thirdpointsflexibletemp
            
        erstepunkte = None
        zweitepunkte = None
        drittepunkte = None
        




    elif functionnumber == "2":


        heretousepoints = pkte[abstandpktzuarray( (anfangspunkt + endpunkt) / 2., pkte) < (abstandanfend / 2. + 
                                                                                           max(FLEXIBLEATSTARTKO, FLEXIBLEATENDKO))]
        #at about 3h running
        #calculate all the lengths that can produce the distance between beginning and end in an rectangular triangle
        linkertriangle = linkerlaengenKO[(linkerlaengenKO - LENGTHOFANGLEKO) < abstandanfend] - LENGTHOFANGLEKO
        linkertriangleone = np.repeat(linkertriangle, np.size(linkertriangle, axis = 0))
        linkertriangletwo = np.tile(linkertriangle, np.size(linkertriangle, axis = 0))

        linkertrianglehypoth = np.sqrt(linkertriangleone ** 2 + linkertriangletwo ** 2)

        keeptriangles = ((linkertrianglehypoth > (abstandanfend - FLEXIBLEATENDKO - FLEXIBLEATSTARTKO)) & 
                         (linkertrianglehypoth < (abstandanfend + FLEXIBLEATENDKO + FLEXIBLEATSTARTKO)))

        linkertriangleone = linkertriangleone[keeptriangles]
        linkertriangletwo = linkertriangletwo[keeptriangles]

        triangleangles = np.around(np.arctan(linkertriangletwo / linkertriangleone), decimals=2)
        #now we produce all the possible points, that lie on a sphere

        displacements = dispnorm * abstandanfend / 2

        allpointsfortriangles =  (anfangspunkt + endpunkt) / 2. + displacements
        amountoftriangles = np.size(allpointsfortriangles, axis = 0)

        anglesintriangle = angle_between_connections_array(np.repeat([endpunkt], amountoftriangles, axis = 0),
                                                           np.repeat([anfangspunkt], amountoftriangles, axis = 0),
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
            


        triangleshiftsbeg = np.float16(make_displacements(FLEXATSTART, dispnormtribeg))


        amountoftriangleshiftsbeg = np.size(triangleshiftsbeg, axis = 0)
        triangleshiftsbeg = np.repeat(triangleshiftsbeg, np.size(allpointsfortriangles, axis = 0), axis = 0)
        allpointsfortriangles = np.tile(allpointsfortriangles, (amountoftriangleshiftsbeg, 1))

        firstpointstriangle  = np.float16(triangleshiftsbeg + anfangspunkt)
        secondpointstriangle = np.float16(triangleshiftsbeg + allpointsfortriangles)


        keep = sort_out_by_length(firstpointstriangle, secondpointstriangle, linkertriangle)

        firstpointstriangle = firstpointstriangle[keep]
        secondpointstriangle = secondpointstriangle[keep]




        MakeSmall = make_small_generator(secondpointstriangle, 12, RAMofclient, ProteinArray = heretousepoints)

        teiler = np.size(secondpointstriangle, axis=0)/(MakeSmall)

        #about 250s per MakeSmall run

        for i in range(0, (MakeSmall +1)):
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
            keep = (distance_from_connection(temp1, temp2, heretousepoints)[0] >= minabstand).all(axis = 1)
            
            temp1 = temp1[keep]    
            temp2 = temp2[keep]
            
            if i == 0:
                firstpointstritemp, secondpointstritemp = temp1, temp2
            else:
                firstpointstritemp = np.concatenate((firstpointstritemp, temp1), axis =0)
                secondpointstritemp = np.concatenate((secondpointstritemp, temp2), axis =0)

            
        firstpointstriangle = firstpointstritemp
        secondpointstriangle = secondpointstritemp



        # In[24]:

        triangleshiftsend = np.float16(make_displacements(FLEXATEND, dispnormtriend))
        #randomize between the ends and the beginning
        amountoftriangleshiftsbeg = np.size(firstpointstriangle, axis = 0)
        amountoftriangleshiftsend = np.size(triangleshiftsend, axis = 0)

        triangleshiftsend = np.tile(triangleshiftsend, (amountoftriangleshiftsbeg, 1))
        firstpointstriangle = np.repeat(firstpointstriangle, amountoftriangleshiftsend, axis = 0)
        secondpointstriangle = np.repeat(secondpointstriangle, amountoftriangleshiftsend, axis = 0)


        # In[25]:

        thirdpointstriangle  = np.float16(triangleshiftsend + endpunkt)


        keep = sort_out_by_length(secondpointstriangle, thirdpointstriangle, linkertriangle)

        firstpointstriangle = firstpointstriangle[keep]
        secondpointstriangle = secondpointstriangle[keep]
        thirdpointstriangle = thirdpointstriangle[keep]




        MakeSmall = make_small_generator(secondpointstriangle, 15, RAMofclient, ProteinArray = heretousepoints)

        teiler = np.size(secondpointstriangle, axis=0)/(MakeSmall)

        #about 250s per MakeSmall run

        for i in range(0, (MakeSmall +1)):
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
            keep = (distance_from_connection(temp2, temp3, heretousepoints)[0] >= minabstand).all(axis = 1)
            
            temp1 = temp1[keep]    
            temp2 = temp2[keep]
            temp3 = temp3[keep]
            
            if i == 0:
                firstpointstritemp, secondpointstritemp, thirdpointstritemp = temp1, temp2, temp3
            else:
                firstpointstritemp = np.concatenate((firstpointstritemp, temp1), axis =0)
                secondpointstritemp = np.concatenate((secondpointstritemp, temp2), axis =0)
                thirdpointstritemp = np.concatenate((thirdpointstritemp, temp3), axis =0)


        firstpointsflexible  = firstpointstritemp
        secondpointsflexible = secondpointstritemp
        thirdpointsflexible  = thirdpointstritemp
        erstepunkte = None
        zweitepunkte = None
        drittepunkte = None


    #evtlraus?: bleiben die hier

    #pickle.dump((firstpointsflexible, secondpointsflexible, thirdpointsflexible), open("files/saveflexibles{projectname}.p".format(projectname = UserDefinedProjectName), "wb"))





    	'''
	    punktetemp = pickle.load( open("files/saveflexibles{projectname}.p".format(projectname = UserDefinedProjectName), "rb" ) )
	    firstpointsflexible  = punktetemp[0]
	    secondpointsflexible = punktetemp[1]
	    thirdpointsflexible  = punktetemp[2]
    	'''




    	#### Flexible ends estimated to make the same as the rigid parts



    	#die verschiebungen mit den Linkerlängen multiplizieren, wichtig ist, in den versch sind immer auch nuller drinnen
    elif functionnumber == "3":
        angleforworkstart = float(angleforworkstart)
        angleforworkend = float(angleforworkend)
        
        versch = make_displacements(linkerlaengenKO, dispnorm)


        anfversch = make_displacements((linkerlaengenKO + FLEXIBLEATSTARTKO - LENGTHOFANGLEKO), startdisp)
        anfversch = anfversch[(anfversch != np.array([0,0,0])).all(axis = 1)]
            
        endversch = make_displacements((linkerlaengenKO + FLEXIBLEATENDKO - LENGTHOFANGLEKO), enddisp)
        endversch = endversch[(endversch != np.array([0,0,0])).all(axis = 1)]

            
        #hier werden die Punkte generiert
        erstepunkte = np.float16(naechstepunkte([anfangspunkt], anfversch)[1])
        erstepunkte = erstepunkte[(erstepunkte == anfangspunkt).all(axis=1) |
                                  aussortierennachpunken(erstepunkte, PointsOfAllSubunits, minabstand, maxabstand)]

        letztepunkte = np.float16(naechstepunkte([endpunkt], endversch)[1])
        letztepunkte = letztepunkte[(letztepunkte == endpunkt).all(axis=1) | 
                                    aussortierennachpunken(letztepunkte, PointsOfAllSubunits, minabstand, maxabstand)]

        #aussortieren, ob Punkte durch Protein gehen
        #we just test with all as but not the first and last, because they are too close.

        #TODO hier abfangen, falls gleich alle Punkte weggemacht werden und dann eine Ausgabe machen, dass das ziemlich schwierig
        #und dann aber weiterfortlaufen, das gleiche auch mit den letzten Punkten



        #wir sortieren erstepunkte aus, die zu weit vom Ende entfernt liegen, sodass sie nicht mehr durch 
        #die doppelte längste Linkerlänge verbunden werden können

        temp = abstandpktzuarray(endpunkt, erstepunkte)
        keep = temp < (3 * laengstesstueck)
        erstepunkte = erstepunkte[keep]

        #wir sortieren erstepunkte aus, die zu weit vom Ende entfernt liegen, sodass sie nicht mehr durch 
        #die doppelte längste Linkerlänge verbunden werden können

        temp = abstandpktzuarray(anfangspunkt, letztepunkte)
        keep = temp < (3 * laengstesstueck)
        letztepunkte = letztepunkte[keep]

        #die zweite iteration, erstepunkte wird so groß gemacht, wie zweitepunkte, damit die Wege passen
        #davor fragen wir ab, ob es überhaupt sinnvoll ist, die eine weitere Ecke zu nehmen, das spart viel Rechenzeit

        if ((abstandanfend < ((3*np.min(linkerlaengenKO)) - (2 * LENGTHOFANGLEKO))) & ((np.max(linkerlaengenKO) * 2 -(2 * LENGTHOFANGLEKO)) > maxvonanfang) & (((np.max(linkerlaengenKO) * 2) - (2 * LENGTHOFANGLEKO)) > maxvonende)):
            zweitepunkte = erstepunkte
        else:
            
            sliceverschstart = int((np.size(versch, axis = 0) - 1) * (angleforworkstart / 100.))
            if angleforworkend != 100:
                sliceverschend = int((np.size(versch, axis = 0) - 1) * (angleforworkend / 100.))
            else:
                sliceverschend = np.size(versch, axis = 0)
            
            zweiteiteration = naechstepunkte(erstepunkte, versch[sliceverschstart:sliceverschend])
            zweitepunkte = np.float16(zweiteiteration[1])
            erstepunkte = np.float16(zweiteiteration[0])

        

        #Nach Winkeln aussortieren, von vorne.

        temp = sort_out_by_angle([anfangspunkt], erstepunkte, zweitepunkte, angletosequence)
        erstepunkte = temp[0]
        zweitepunkte = temp[1]


        #wir sortieren zweite Punkte aus, die zu weit vom Ende entfernt liegen, sodass sie nicht mehr durch 
        #die doppelte längste Linkerlänge verbunden werden können

        temp = abstandpktzuarray(endpunkt, zweitepunkte)
        keep = temp < (2 * laengstesstueck)
        zweitepunkte = zweitepunkte[keep]
        erstepunkte = erstepunkte[keep]

        #Läuft 82 sek, sortiert 60 000 Punkte aus
        #wir sortieren die Punkte aus, die zu weit oder zu nah im Protein sind

        MakeSmall = make_small_generator(zweitepunkte,1 , RAMofclient , ProteinArray = PointsOfAllSubunits)
        teiler = np.size(zweitepunkte, axis = 0)/MakeSmall
        temp = aussortierennachpunken(zweitepunkte[:teiler], PointsOfAllSubunits, minabstand, maxabstand)

        for i in range(1,MakeSmall):
            temp = np.concatenate((temp, aussortierennachpunken(zweitepunkte[i*teiler:(i+1)*teiler],                                                        PointsOfAllSubunits, minabstand, maxabstand)), axis = 0)
        if ((i+1) * teiler) < np.size(zweitepunkte, axis=0): 
            temp = np.concatenate((temp, aussortierennachpunken(zweitepunkte[(i+1)*teiler:],
                                                                PointsOfAllSubunits, minabstand, maxabstand)), axis = 0)

        temp = np.array(temp)
        temp = np.ravel(temp, "C")

        zweitepunkte = zweitepunkte[temp]
        erstepunkte = erstepunkte[temp]
       
        #evtlraus
        #save for saving calculationtime
        #pickle.dump((erstepunkte, zweitepunkte, letztepunkte),            open("files/save{projectname}.p".format(projectname = UserDefinedProjectName), "wb"))

        """
        punktetemp = pickle.load( open("files/save{projectname}.p".format(projectname = UserDefinedProjectName), "rb" ) )
        erstepunkte = punktetemp[0]
        zweitepunkte = punktetemp[1]
        letztepunkte = punktetemp[2]
        """

        #läuft etwa 11 minuten, reduziert um die Hälfte
        MakeSmall = make_small_generator(zweitepunkte, 10 , RAMofclient , ProteinArray = PointsOfAllSubunits)

        teiler = np.size(zweitepunkte, axis=0)/(MakeSmall)
        temp = sort_out_by_protein(erstepunkte[:teiler], zweitepunkte[:teiler], PointsOfAllSubunits, minabstand)
        erstetemp = temp[0]
        zweitetemp = temp[1]



        #das läuft zu lange...
        for i in range(1, MakeSmall):
            temp = sort_out_by_protein(erstepunkte[i*teiler:(i+1)*teiler], zweitepunkte[i*teiler:(i+1)*teiler],                        PointsOfAllSubunits, minabstand)
            
            erstetemp = np.concatenate((erstetemp, temp[0]), axis =0)
            zweitetemp = np.concatenate((zweitetemp, temp[1]), axis =0)
            

        if ((i+1) * teiler) < np.size(zweitepunkte, axis=0):    
            temp = sort_out_by_protein(erstepunkte[(i+1)*teiler:], zweitepunkte[(i+1)*teiler:], PointsOfAllSubunits, minabstand)

            erstetemp = np.concatenate((erstetemp, temp[0]), axis = 0)
            zweitetemp = np.concatenate((zweitetemp, temp[1]), axis = 0)

        erstepunkte = np.float16(erstetemp)
        zweitepunkte = np.float16(zweitetemp)

        #evtlraus

        #pickle.dump((erstepunkte, zweitepunkte, letztepunkte), open("files/save{projectname}.p".format(projectname = UserDefinedProjectName), "wb"))




        """
        punktetemp = pickle.load( open("files/save{projectname}.p".format(projectname = UserDefinedProjectName), "rb" ) )
        erstepunkte = punktetemp[0]
        zweitepunkte = punktetemp[1]
        letztepunkte = punktetemp[2]
        """


        ###### Generierung der Verbindungen zwsichen den zweiten und den dritten Punkten



        MakeSmall = make_small_generator(zweitepunkte,8 , RAMofclient , ProteinArray = letztepunkte)

        teiler = np.size(zweitepunkte, axis=0)/(MakeSmall)


        if os.path.exists('files/data{projectname}.h5'.format(projectname = UserDefinedProjectName)):
            os.remove('files/data{projectname}.h5'.format(projectname = UserDefinedProjectName))
        h5f = h5py.File('files/data{projectname}.h5'.format(projectname = UserDefinedProjectName), "w")


        for laenge in linkerlaengenKO:
            
            for i in range(0,(MakeSmall)):
                          
                temp = sort_out_by_distance(zweitepunkte[i*teiler:(i+1)*teiler], letztepunkte, erstepunkte[i*teiler:(i+1)*teiler], laenge, hitgenauig)
                if i == 0:
                    erstetemp = temp[0]
                    zweitetemp= temp[1]
                    drittetemp= temp[2]
                else:
                    erstetemp = np.concatenate((erstetemp, temp[0]), axis =0)
                    zweitetemp = np.concatenate((zweitetemp, temp[1]), axis =0)
                    drittetemp = np.concatenate((drittetemp, temp[2]), axis =0)
                    
            if ((i+1) * teiler) < np.size(zweitepunkte, axis=0):  
                temp = sort_out_by_distance(zweitepunkte[(i+1)*teiler:], letztepunkte, erstepunkte[(i+1)*teiler:], laenge, hitgenauig)
                erstetemp = np.concatenate((erstetemp, temp[0]), axis =0)
                zweitetemp = np.concatenate((zweitetemp, temp[1]), axis =0)
                drittetemp = np.concatenate((drittetemp, temp[2]), axis =0)
            
            count = 1
            for array in [erstetemp, zweitetemp, drittetemp]:
                h5f.create_dataset("dataset_{points}{linker}".format(points = count, linker = int(laenge)), data=array)
                count +=1

        h5f.close()



        h5f = h5py.File('files/data{projectname}.h5'.format(projectname = UserDefinedProjectName),'r')



        for laenge in linkerlaengenKO:
            
            SizeOfArray = len(h5f["dataset_{points}{linker}".format(points = 1, linker = int(laenge))]) * 3
            
            
            MakeSmall = make_small_generator(SizeOfArray,12 , RAMofclient , ProteinArray = PointsOfAllSubunits)
            teiler = SizeOfArray/(MakeSmall * 3)
            
            
            erstepunkte  = h5f["dataset_{points}{linker}".format(points = 1, linker = int(laenge))][:teiler]
            zweitepunkte = h5f["dataset_{points}{linker}".format(points = 2, linker = int(laenge))][:teiler]
            drittepunkte = h5f["dataset_{points}{linker}".format(points = 3, linker = int(laenge))][:teiler]

            temp = sort_out_by_protein(zweitepunkte, drittepunkte, PointsOfAllSubunits, minabstand, beforearray = erstepunkte)
            erstetemp = temp[0]
            zweitetemp = temp[1]
            drittetemp = temp[2]



            
            #das läuft zu lange, ein Durchlauf 2.5s, das heißt insgesamt: 30500~9hs
            for i in range(1, MakeSmall):
                erstepunkte  = h5f["dataset_{points}{linker}".format(points = 1, linker = int(laenge))][i * teiler:(i+1)*teiler]
                zweitepunkte = h5f["dataset_{points}{linker}".format(points = 2, linker = int(laenge))][i * teiler:(i+1)*teiler]
                drittepunkte = h5f["dataset_{points}{linker}".format(points = 3, linker = int(laenge))][i * teiler:(i+1)*teiler]
                temp = sort_out_by_protein(zweitepunkte, drittepunkte,                                PointsOfAllSubunits, minabstand, beforearray = erstepunkte)

                erstetemp = np.concatenate((erstetemp, temp[0]), axis =0)
                zweitetemp = np.concatenate((zweitetemp, temp[1]), axis =0)
                drittetemp = np.concatenate((drittetemp, temp[2]), axis =0)
                
                
            if ((i+1) * teiler) < (SizeOfArray / 3):  
                erstepunkte  = h5f["dataset_{points}{linker}".format(points = 1, linker = int(laenge))][(i+1) * teiler:]
                zweitepunkte = h5f["dataset_{points}{linker}".format(points = 2, linker = int(laenge))][(i+1) * teiler:]
                drittepunkte = h5f["dataset_{points}{linker}".format(points = 3, linker = int(laenge))][(i+1) * teiler:]


                temp = sort_out_by_protein(zweitepunkte, drittepunkte,                                    PointsOfAllSubunits, minabstand, beforearray = erstepunkte)

                erstetemp = np.concatenate((erstetemp, temp[0]), axis = 0)
                zweitetemp = np.concatenate((zweitetemp, temp[1]), axis = 0)
                drittetemp = np.concatenate((drittetemp, temp[2]), axis = 0)
            
            

        erstepunkte = np.float16(erstetemp)
        zweitepunkte = np.float16(zweitetemp)
        drittepunkte = np.float16(drittetemp)

            
            

        h5f.close()
            






        tempsize =  np.size(erstepunkte, axis = 0)
        '''
        pickle.dump(erstepunkte[:tempsize/2],             open("files/save{projectname}ersteeins.p".format(projectname = UserDefinedProjectName), "wb"))
        pickle.dump(erstepunkte[tempsize/2:],             open("files/save{projectname}erstezwei.p".format(projectname = UserDefinedProjectName), "wb"))
        pickle.dump(zweitepunkte[:tempsize/2],             open("files/save{projectname}zweiteeins.p".format(projectname = UserDefinedProjectName), "wb"))
        pickle.dump(zweitepunkte[tempsize/2:],             open("files/save{projectname}zweitezwei.p".format(projectname = UserDefinedProjectName), "wb"))
        pickle.dump(drittepunkte[:tempsize/2],             open("files/save{projectname}dritteeins.p".format(projectname = UserDefinedProjectName), "wb"))
        pickle.dump(drittepunkte[tempsize/2:],             open("files/save{projectname}drittezwei.p".format(projectname = UserDefinedProjectName), "wb"))
        '''


        #evtlraus

        '''
        erstepunkteeins = pickle.load( open( "files/save{projectname}ersteeins.p".format(projectname = UserDefinedProjectName), "rb" ) )
        erstepunktezwei = pickle.load( open( "files/save{projectname}erstezwei.p".format(projectname = UserDefinedProjectName), "rb" ) )
        erstepunkte = np.concatenate((erstepunkteeins, erstepunktezwei), axis = 0)

        zweitepunkteeins = pickle.load( open( "files/save{projectname}zweiteeins.p".format(projectname = UserDefinedProjectName), "rb" ) )
        zweitepunktezwei = pickle.load( open( "files/save{projectname}zweitezwei.p".format(projectname = UserDefinedProjectName), "rb" ) )
        zweitepunkte = np.concatenate((zweitepunkteeins, zweitepunktezwei), axis = 0)

        drittepunkteeins = pickle.load( open("files/save{projectname}dritteeins.p".format(projectname = UserDefinedProjectName), "rb"))
        drittepunktezwei = pickle.load( open("files/save{projectname}drittezwei.p".format(projectname = UserDefinedProjectName), "rb"))
        drittepunkte = np.concatenate((drittepunkteeins, drittepunktezwei), axis = 0)
        '''




        if ((abstandanfend < 3*np.min(linkerlaengenKO)) & (np.max(linkerlaengenKO) * 2 > maxvonanfang)    & (np.max(linkerlaengenKO) * 2 > maxvonende)):
            temp = sort_out_by_angle([anfangspunkt], zweitepunkte, drittepunkte, angletosequence)
            erstepunkte = temp[0]
            zweitepunkte = temp[0]
            drittepunkte = temp[1]
        else:
            temp = sort_out_by_angle(erstepunkte, zweitepunkte, drittepunkte, angletosequence)
            erstepunkte = temp[0]
            zweitepunkte = temp[1]
            drittepunkte = temp[2]


        #evtlraus

        #pickle.dump((erstepunkte, zweitepunkte, drittepunkte), open("files/save{projectname}.p".format(projectname = UserDefinedProjectName), "wb"))
        
        firstpointsflexible = None
        secondpointsflexible = None
        thirdpointsflexible = None



    '''
    punktetemp = pickle.load( open("files/save{projectname}.p".format(projectname = UserDefinedProjectName), "rb" ) )
    erstepunkte = punktetemp[0]
    zweitepunkte = punktetemp[1]
    drittepunkte = punktetemp[2]
    '''


    '''
    punktetemp = pickle.load( open("files/saveflexibles{projectname}.p".format(projectname = UserDefinedProjectName), "rb" ) )
    firstpointsflexible  = punktetemp[0]
    secondpointsflexible = punktetemp[1]
    thirdpointsflexible  = punktetemp[2]
    '''

    if firstpointsflexible != None:

        firstpointsflexible, secondpointsflexible, thirdpointsflexible = make_better_paths_flex(firstpointsflexible,
                                                                                                secondpointsflexible,
                                                                                                thirdpointsflexible, endpunkt)
    if erstepunkte != None:
        erstepunkte, zweitepunkte, drittepunkte = make_better_paths_rigid(anfangspunkt, erstepunkte, zweitepunkte, drittepunkte,
                                                                          endpunkt)



    #### Die Bewertungsfunktion 

    # Wir definieren Regionen, die schlecht für den Linker sind. Dabei bekommt jede Region eine Güte. Diese Güte sagt, wenn wir einen Linker in einem Abstand von Güte geteilt durch Minabstand vorbeigehen lassen. Das heißt je kleiner die Güte, desto näher kann ich an diesem Punkt vorbei gehen.
    # 
    # Im Allgemeinen möchte ich, dass einfach immer die verschiedenen Teile gleich wichtig sind, egal wie groß das Protein ist, oder wie viele Regionen wir da gesagt haben, dass umgangen werden sollen.
    # 
    # Bei den Winkeln haben wir ja immer maximal drei Winkel, von dem her, muss das nicht normiert werden.
    # 
    # Bei der Länge wird mit dem Abstand der Enden skaliert, bei den unguten Regionen wird so skaliert, dass egal wie viele es sind, die definiert wurden, immer insgesamt die Gewichtung 1 ist.

    # In[69]:

    #Userstring ist von der Form: 273,10 280-290,5 298,7,35.6  usw. (Leerzeichen trennen Einträge, , for single residues
    #- for ranges, second, for the diameter of the substrate)



    #UserdefinedWeighing = "19,10,10" #Lambdalysozyme
    UserdefinedWeighing = ""



    ShouldBeWeighed, Weighingarray, substratelist = make_weighingarrays(UserdefinedWeighing)

    if secondpointsflexible != None:
        if np.size(secondpointsflexible, axis = 0) > 0:


            MakeSmall = make_small_generator(secondpointsflexible, 8 , RAMofclient , ProteinArray = pkte)

            teiler = np.size(secondpointsflexible, axis=0)/(MakeSmall)
            

            temp = weighing_function_flex(anfangspunkt, firstpointsflexible[:teiler], secondpointsflexible[:teiler],
                                            thirdpointsflexible[:teiler], endpunkt, pkte, InterestingAANr,\
                                  ShouldBeWeighed, Weighingarray, substratelist)

            knull = temp[0]
            keins = temp[1]
            kzwei = temp[2]
            kdrei = temp[3]
            kvier = temp[4]


            for i in range(1, MakeSmall):
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





            weightflex = np.array([knull, keins, kzwei, kdrei, kvier])
            flexk = weightflex
        else:
            weightflex = None
    else:
        weightflex = None


    #weighting of linkers without flexible ends
    if zweitepunkte != None:
        if np.size(zweitepunkte, axis = 0) > 0:

            MakeSmall = make_small_generator(zweitepunkte, 8 , RAMofclient , ProteinArray = pkte)

            teiler = np.size(zweitepunkte, axis=0)/(MakeSmall)

            temp = weighing_function_rigids(anfangspunkt, erstepunkte[:teiler], zweitepunkte[:teiler],
                                            drittepunkte[:teiler], endpunkt, pkte, InterestingAANr,\
                                  ShouldBeWeighed, Weighingarray, substratelist)

            knull = temp[0]
            keins = temp[1]
            kzwei = temp[2]
            kdrei = temp[3]
            kvier = temp[4]


            for i in range(1, MakeSmall):
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




            weightrig = np.array([knull, keins, kzwei, kdrei, kvier])
            k = weightrig
        else:
            weightrig = None
    else:
        weightrig = None


    # At first the different linkers are just analysed. Of course this could be done in the weighing step before, but this is not that calculation intensive and like this it is much more clear when it does what.

    sequences, weightingsall, firstpointsall, secondpointsall, thirdpointsall =translate_paths_to_sequences(anfangspunkt,firstpointsflexible, secondpointsflexible,
                                                        thirdpointsflexible, erstepunkte, zweitepunkte, drittepunkte, 
                                                        endpunkt, linkerdatenbank, linkerlaengenKO, angletosequence, 
                                                        angleseparators, weightflex, weightrig)


    f = open(resultfile, "w")

    f.write("sequence,erstepunkteallx,erstepunkteally,erstepunkteallz,zweitepunkteallx,zweitepunkteally,zweitepunkteallz,drittepunkteallx,drittepunkteally,drittepunkteallz,lengthofpath,weightingofangles,unpreferableplaces,distfromsurface\n")
    for i in range(np.size(sequences)):
        writestring = sequences[i]
        for j in range(3):
            writestring += "," + str(firstpointsall[i][j])
        for j in range(3):
            writestring += "," + str(secondpointsall[i][j])
        for j in range(3):
            writestring += "," + str(thirdpointsall[i][j])
        for j in range(1,np.size(weightingsall, axis = 0)):
            writestring += "," + str(weightingsall[j][i])
        writestring += "\n"
        
        f.write(writestring)
        

    f.close()
