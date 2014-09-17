# This Python file uses the following encoding: utf-8

import numpy as np
import matplotlib
matplotlib.use("GTK")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
from matplotlib import rc
from globals import *


matplotlib.rc("axes", titlesize      = "Large", labelsize      ="Large" )

def define_globals(date, folder, kind,  upperlimit, lowerlimit, legendplace, ignorelist):
    global DATE
    global UPPERLIMIT
    global LOWERLIMIT
    global FOLDER
    global KIND
    global LEGENDPLACE
    global IGNORELIST
    
    UPPERLIMIT = upperlimit
    LOWERLIMIT = lowerlimit
    FOLDER = folder
    DATE = date
    KIND = kind
    LEGENDPLACE = legendplace
    IGNORELIST = ignorelist

def fitfunc(x, A, lam, C):
    return A * np.exp( - lam * x) + C

def make_plots(thedict, coordtoindict, plotlisttuple = None, fitdict = None):
    """
Creates histograms of the distribution of all turn sequences, 
always a histogram for the distance and for the angles is
produced. These are saved in the folder called path.

Plotslisttuple always needs a list of the coordinates and a string of the file's name
    """
    

    
    if plotlisttuple == None:
        x = thedict["time"]
        for key in thedict:
            if (key != "time" ) & (key != "measuretemperature") & (key != "calibration") & (key not in IGNORELIST):
            
                y = thedict[key]  
                plt.plot(x, y, "bo", ms=10)
                plt.title("OD600 of {well}".format(well = key + "_with:_" + coordtoindict[key]  + DATE))
                plt.xlabel("time in [min]")
                if KIND == "Nils_":
                    plt.ylabel("Optical Density at 600 nm")
                elif KIND == "Fluo_":
                    plt.ylabel("Fluorescence")
                #plt.yscale("log")
                if max(y) > UPPERLIMIT:
                    plt.ylim(ymin = LOWERLIMIT)
                else:
                    plt.ylim((LOWERLIMIT, UPPERLIMIT))

                if fitdict != None:
                    try:
                        #the fitting
                        popt, pcov = curve_fit(fitfunc, x, y)

                        x_fit = np.linspace(0., x[-1] + 10, 100)
                        y_fit = fitfunc(x_fit, *popt)
                        y_mod = fitfunc(x, *popt)
                        #chi squared
                        redchisq = redchisqg(y, y_mod, deg = 3)
                        slope = popt[1]
                        try:
                            slopeerr = pcov[1,1]
                        except:
                            slopeerr = None
                        plt.plot(x_fit, y_fit, "r--", lw = 3,   
                                 label="fit at red $\chi^2$ = " + "{chisq:5.2f}".format(chisq = redchisq))
                        plt.text(0.9 * x[-1], np.mean(y), "slope : {steig}".format(steig = slope))
                        
                        lg = plt.legend(loc = 'upper right', bbox_to_anchor = (LEGENDPLACE, 1))
                        if lg != None:
                            lg.draw_frame(False)
                    except:
                        redchisq = None
                        slope = None
                        slopeerr = None
                        
                    #sort out misfitted
                    if slopeerr > 0.1:
                        redchisq = None
                        slope = None
                        slopeerr = None
                    fitdict[key] = [slope, slopeerr, redchisq]
                else:
                    lg = None
                
                if (not os.path.exists(FOLDER + "automated_plots")):
                    os.makedirs(FOLDER + "automated_plots")
                if lg == None:
                    plt.savefig(FOLDER + "automated_plots/plot_of_{well}.png".format(well = key + "_with_" +
                                                                                     coordtoindict[key]  + DATE), dpi = 200)
                else:
                    plt.savefig(FOLDER + "automated_plots/plot_of_{well}.png".format(well = key + "_with_" +
                                                                                     coordtoindict[key]  + DATE),
                                bbox_extra_artists=(lg,), bbox_inches='tight', dpi = 200)
                plt.close()
        if fitdict != None:
            return fitdict
            
            
    else:
        plotlist = plotlisttuple[0]
        maxcount = False
        
        x = thedict["time"]
        count = 0
        for key in plotlist:
            y = thedict[key]
            if max(y) > UPPERLIMIT:
                maxcount = True
                
            if count < 7:
                plt.plot(x, y, label = "{well}".format(well = key + "with" + coordtoindict[key]), lw = 3.)
            elif count < 14:
                plt.plot(x, y, "x",  label = "{well}".format(well = key + "with" + coordtoindict[key]), ms=10.)
            else:
                plt.plot(x, y, "o",  label = "{well}".format(well = key + "with" + coordtoindict[key]), ms=10.)
            count += 1
            
            
            if fitdict != None:
                try:
                    #the fitting
                    popt, pcov = curve_fit(fitfunc, x, y)

                    x_fit = np.linspace(0., x[-1] + 10, 100)
                    y_fit = fitfunc(x_fit, *popt)
                    y_mod = fitfunc(x, *popt)
                    #chi square
                    redchisq = redchisqg(y, y_mod, deg = 3)
                    slope = popt[1]
                    try:
                        slopeerr = pcov[1,1]
                    except:
                        slopeerr = None
                    plt.plot(x_fit, y_fit, lw = 3,   
                             label="fit at red $\chi^2$ = " + "{chisq:5.2f}".format(chisq = redchisq))
                    
                except:
                    redchisq = None
                    slope = None
                    slopeerr = None
        if maxcount:
            plt.ylim(ymin = LOWERLIMIT)
        else:
            plt.ylim((LOWERLIMIT, UPPERLIMIT))
            
        plt.title("{well}".format(well = plotlisttuple[1]))
        plt.xlabel("time in [min]")
        if KIND == "Nils_":
            plt.ylabel("Optical Density at 600 nm")
        elif KIND == "Fluo_":
            plt.ylabel("Fluorescence")        
        lg = plt.legend(loc = 'upper right', bbox_to_anchor = (LEGENDPLACE, 1))
        if lg != None:
            lg.draw_frame(False)
        #plt.yscale("log")
        plt.savefig( FOLDER + "plot_of_{well}.png".format(well = plotlisttuple[1] + DATE),bbox_extra_artists=(lg,),
                    bbox_inches='tight', dpi=200)
        plt.close()    
        
        
def redchisqg(ydata,ymod,deg=2,sd=None):
    """  
Returns the reduced chi-square error statistic for an arbitrary model,   
chisq/nu, where nu is the number of degrees of freedom. If individual   
standard deviations (array sd) are supplied, then the chi-square error   
statistic is computed as the sum of squared errors divided by the standard   
deviations. See http://en.wikipedia.org/wiki/Goodness_of_fit for reference.  

ydata,ymod,sd assumed to be Numpy arrays. deg integer.  

Usage:  
>>> chisq=redchisqg(ydata,ymod,n,sd)  
where  
ydata : data  
ymod : model evaluated at the same x points as ydata  
n : number of free parameters in the model  
sd : uncertainties in ydata  

Rodrigo Nemmen  
http://goo.gl/8S1Oo  
   """  
      # Chi-square statistic  
    if sd==None:  
       chisq=np.sum((ydata-ymod)**2 / ydata)  
    else:  
       chisq=np.sum( ((ydata-ymod)/sd)**2 / ydata)  
         
    # Number of degrees of freedom assuming 2 free parameters  
    nu=len(ydata)-1-deg  
    
    return chisq/nu    
    
    
    
def make_plots_from_datalist(datalist, timelist, nameofplot, fitdict = None):
    global UPPERLIMIT
    global LOWERLIMIT
    global FOLDER

    '''
    datalist is a list of datatuples with mean values, errors and name in this sequence
    '''
    
    maxcount = False

    x = timelist
    count = 0
    for tuplehere in datalist:
        y = tuplehere[0]
        if max(y) > UPPERLIMIT:
            maxcount = True

        if count < 7:
            plt.errorbar(x, y, elinewidth=1, yerr=tuplehere[1], label = "{well}".format(well = tuplehere[2]), lw = 3.)
        elif count < 14:
            plt.errorbar(x, y, elinewidth=1, fmt = "x", yerr=tuplehere[1], label = "{well}".format(well = tuplehere[2]), ms=10.)
        else:
            plt.errorbar(x, y, elinewidth=1, fmt = "o", yerr=tuplehere[1], label = "{well}".format(well = tuplehere[2]), ms=10.)
        count += 1
        #plt.errorbar(x, y, yerr=tuplehere[1], fmt = None)


        if fitdict != None:
            try:
                #the fitting
                popt, pcov = curve_fit(fitfunc, x, y)

                x_fit = np.linspace(0., x[-1] + 10, 100)
                y_fit = fitfunc(x_fit, *popt)
                y_mod = fitfunc(x, *popt)
                #chi square
                redchisq = redchisqg(y, y_mod, deg = 3)
                slope = popt[1]
                try:
                    slopeerr = pcov[1,1]
                except:
                    slopeerr = None
                plt.plot(x_fit, y_fit, lw = 3,   
                         label="fit at red  $\chi^2$ = " + "{chisq:5.2f}".format(chisq = redchisq))

            except:
                redchisq = None
                slope = None
                slopeerr = None
    if maxcount:
        plt.ylim(ymin = LOWERLIMIT)
    else:
        plt.ylim((LOWERLIMIT, UPPERLIMIT))

    plt.title("{well}".format(well = nameofplot + DATE))
    plt.xlabel("time in [min]")
    
    if KIND == "Nils_":
        plt.ylabel("Optical Density at 600 nm")
    elif KIND == "Fluo_":
        plt.ylabel("Fluorescence") 
               
    lg = plt.legend(loc = 'upper right', bbox_to_anchor = (LEGENDPLACE, 1))
    if lg != None:
        lg.draw_frame(False)
    #plt.yscale("log")
    plt.savefig( FOLDER + "plot_of_{well}.png".format(well = nameofplot + DATE),bbox_extra_artists=(lg,),
                bbox_inches='tight', dpi=200)
    plt.close()
    
def make_calibration_plot(datadict):
    datadict["calibration"] = np.array(datadict["calibration"], dtype=float)
    datadict["calibration"] = np.reshape(datadict["calibration"], (8, 12))

    fig = plt.figure()
    ax = plt.axes()
    H = ax.pcolor(datadict["calibration"])
    plt.ylabel("y-axis")
    plt.xlabel("x-axis")
    plt.gca().invert_yaxis()
    fig.colorbar(H)
    plt.savefig( FOLDER + "plot_of_plate_before_lyse.png", dpi=200)
    plt.close()
    
def make_temperature_plot(datadict):
        
    '''
    makes and saves a plot of temperatures when was measured.
    '''
    
    plt.plot(datadict["time"], datadict["measuretemperature"], "r-")


    plt.title("Temperature")
    plt.xlabel("time in [min]")
    plt.ylabel("Temperature in [$\degree$C]")        
    plt.savefig( FOLDER + "plot_of_temperature_behaviour.png", dpi=200)
    plt.close()
    
    
    
def make_plots_on_axis(datadict, equivalentaxesdict, totalredundanciesdict, coordtoinputdict, coordx, coordy):
    """
makes plots on all the axis, if two axis are exactly the same, they are combined.
    """
    skiplistx = []
    for x in coordx:
        datalist = []
        alreadylistx = [] #with coordinates
        if x not in skiplistx:
            skiplistx = skiplistx + equivalentaxesdict[x]
            skiplisttotal = []
            for y in coordy:
                if ((y + x) not in skiplisttotal) & ((y + x) not in IGNORELIST):
                    plotlist = []
                    for eq in totalredundanciesdict[y + x]:
                        skiplisttotal.append(eq)
                        plotlist.append(eq)
                    medarray, erraray = medium_of_wells(plotlist, datadict)
                    datalist.append((medarray, erraray, coordtoinputdict[plotlist[0]]))
            make_plots_from_datalist(datalist, datadict["time"], "{this}_axis".format(this = x))
        
    skiplisty = []
    for y in coordy:
        datalist = []
        alreadylisty = [] #with coordinates
        if y not in skiplisty:
            skiplisty = skiplisty + equivalentaxesdict[y]
            skiplisttotal = []
            for x in coordx:
                if ((y + x) not in skiplisttotal) & ((y + x) not in IGNORELIST):
                    plotlist = []
                    for eq in totalredundanciesdict[y + x]:
                        skiplisttotal.append(eq)
                        plotlist.append(eq)
                    medarray, erraray = medium_of_wells(plotlist, datadict)
                    datalist.append((medarray, erraray, coordtoinputdict[plotlist[0]]))
            make_plots_from_datalist(datalist, datadict["time"], "{this}_axis".format(this = y))
            
            
            
def medium_of_wells(welltuple, datadict):
    '''
    returns a two arrays, the medium and the std array
    '''
    
    for well in welltuple:
        if well not in IGNORELIST:
            if well == welltuple[0]:
                calcarray = np.array([datadict[well]])
            else:
                calcarray = np.append(calcarray,  np.array([datadict[well]]), axis = 0)
    medarray = np.mean(calcarray, axis = 0)
    errarray = np.std(calcarray, axis = 0)
    return medarray, errarray



def get_coord_with_properties(whatiswheredict, kind, value):
    '''
    takes a kind like "temperature" and a value and returns an array of coordinates, that have this property
    '''
    retlist = []
    for key in whatiswheredict[kind]:
        if (whatiswheredict[kind][key] == value):
            retlist.append(key)
    return np.array(retlist)
    
    
def lysozyme_activity_plot(dictoftoplottypes, whatiswheredict, fitdict):
    '''
    generates a plot of all the lysozyme activities to the temperatures. 
    '''
    #the activity
    lystypelist = []
    for lystype in dictoftoplottypes:

        lystypelist.append(lystype)
    lystypelist.sort()
    count = 0
    
    for lystype in lystypelist:
        x = []
        y = []
        yerr = []
        for key in dictoftoplottypes[lystype]:
            if key not in IGNORELIST:
                x.append(float(whatiswheredict["temperature"][key]))
                y.append(fitdict[key][0])
                yerr.append( fitdict[key][1])   
        x  = np.array(x)
        y = np.array(y)
        yerr = np.array(yerr)

        keep = (y > 0) & (yerr > 0)
        x = x[keep]
        y = y[keep]
        yerr = yerr[keep]

        ynormed = y / np.max(y)
        yerrnormed = y / np.max(y)

        if count < 7:
            plt.plot(x, y, "o", label = lystype, ms=10.)
        else:
            plt.plot(x, y, "x", label = lystype, ms=10.)
        count += 1

        plt.errorbar(x, y, yerr = yerr, fmt=None)

    plt.xlabel("temperature [°C]")
    plt.ylabel("activity [1/min]")



    lg = plt.legend(loc = 'upper right', bbox_to_anchor = (1.3, 1))
    if lg != None:
        lg.draw_frame(False)
    plt.savefig(FOLDER + "resultsplotlamlys.png", bbox_extra_artists=(lg,), bbox_inches='tight', dpi = 200)    
    plt.close()
    
    
def lysozyme_activity_plot_normed(dictoftoplottypes, whatiswheredict, fitdict):
    
    '''
    generates a normed acitvity plot of the types, defined in dictoftoplottypes
    '''
    
    lystypelist = []
    for lystype in dictoftoplottypes:

        lystypelist.append(lystype)
    lystypelist.sort()
    count = 0

    for lystype in lystypelist:
        x = []
        y = []
        yerr = []
        for key in dictoftoplottypes[lystype]:
            if key not in IGNORELIST:
                x.append(float(whatiswheredict["temperature"][key]))
                y.append(fitdict[key][0])  
        x  = np.array(x)
        y = np.array(y)

        keep = (y > 0) & (yerr > 0)
        x = x[keep]
        y = y[keep]

        sortarray = np.argsort(x)
        x = x[sortarray]
        y = y[sortarray]
        
        sameys = []
        newylist = []
        newxlist = []
        newyerrlist = []
        for i in range(0,np.size(x)):
            if i == 0:
                sameys.append(y[0])
            else:
                if x[i] == x[i-1]:
                    sameys.append(y[i])
                else:
                    newxlist.append(x[i-1])
                    sameys = np.array(sameys)
                    newylist.append(np.mean(sameys))
                    newyerrlist.append(np.std(sameys))
                    sameys = [y[i]]
        newylist = np.array(newylist)
        ynormed = newylist / np.max(newylist)

        if count < 7:
            plt.plot(newxlist, ynormed, "o", label = lystype, ms=15.)
        else:
            plt.plot(newxlist, ynormed, "x", label = lystype, ms=15.)
        count += 1
        plt.ylim(ymin = 0, ymax = 1.1)
        plt.errorbar(newxlist, ynormed, yerr = newyerrlist, fmt=None)

    plt.xlabel("temperature [°C]")
    plt.ylabel("normed activity [1/min]")



    lg = plt.legend(loc = 'upper right', bbox_to_anchor = (1.3, 1))
    if lg != None:
        lg.draw_frame(False)
    plt.savefig(FOLDER + "resultsplotlamlysnormed.png", bbox_extra_artists=(lg,), bbox_inches='tight', dpi = 200)    
    plt.close()
