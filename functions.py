# This Python file uses the following encoding: utf-8

import numpy as np
import matplotlib
matplotlib.use("GTK")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import lambertw
import os
from matplotlib import rc
from globals import *



matplotlib.rc("axes", titlesize      = "Large", labelsize      ="Large" )


def simpleaxis(ax):
    '''
    removes the upper and right axis from a plot
    '''

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

def define_globals(date, folder, kind,  upperlimit, lowerlimit, legendplace, ignorelist):
    global DATE
    global UPPERLIMIT
    global LOWERLIMIT
    global FOLDER
    global KIND
    global LEGENDPLACE
    global IGNORELIST
    global RESULTFOLDER

    RESULTFOLDER = "./only_resultplots/"
    UPPERLIMIT = upperlimit
    LOWERLIMIT = lowerlimit
    FOLDER = folder
    DATE = date
    KIND = kind
    LEGENDPLACE = legendplace
    IGNORELIST = ignorelist

def exp(x, A, lam, C):
    return A * np.exp( - lam * x) + C



def simpleaxis(ax):
    '''
    removes upper and right axis of an axis element
    '''

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()




def my_fitting(x, y, fitdict, ax, key = None):

    '''
    adds a fitted curve to the plot.
    returns a new fitdict, if key is set.
    '''

    OD0 = y[0]
    #a = np.mean(y[-30:])
    m = 1/1.160 #mg/ml

    def fitfunc(t, KM, VMax, a):

        if (KM < 10) & (KM > 0) & (VMax > 0) & (VMax < 1):

            S0 = m * (OD0 - a)

            S =  KM * np.real(lambertw((S0 / KM) * np.exp((S0 - (VMax *t)) / KM) ))
            OD = (S / m) +a

            return OD
        else:
            return 1e10

    def exp_fit(t, VMax, OD0, a):
        return (OD0 -a) * np.exp(-VMax * t) + a


    #plt.plot(make_param(y[1:6], x[1:6], a, OD0), make_result(y[1:6], x[1:6], m, OD0), "bo")
    #plt.xlim(xmin = 0)
    #plt.ylim(ymin = 0)
    #the fitting
    try:
        popt, pcov = curve_fit(fitfunc, x, y, p0 = (0.01, 0.01, np.min(y)))

        KMfit, VMaxfit, afit,  =  popt
        KMfiterr, VMaxfiterr, afiterr =  np.sqrt(np.diag(pcov))
        OD_mod = fitfunc(x, *popt)


        redchisqMM = redchisqg(y, OD_mod, deg = 3)
        ax.plot(x, fitfunc(x, *popt), "r--", lw = 3)

        #plt.plot(x, fitfunc(x, 0.05, np.min(y)), "y--", lw = 3)
        #plt.plot(x, fitfunc(x, KMfit-KMfiterr, VMaxfit - VMaxfiterr, afit - afiterr), "g--", lw = 3)
        #plt.plot(x, fitfunc(x, KMfit+KMfiterr, VMaxfit + VMaxfiterr, afit + afiterr), "g--", lw = 3)
        plt.text(0.8 * x[-1], np.mean(y), "$V_{max MM}$ " + " = {Vmax:5.3f} +- {Vmaxerr:5.3f}".format(Vmax = VMaxfit,
                                                                                               Vmaxerr = VMaxfiterr))
        plt.text(0.8 * x[-1], np.mean(y)-0.1, "$V_{max MM}$" + " = {Vmax:5.3f} +- {Vmaxerr:5.3f}".format(Vmax = VMaxfit,
                                                                                               Vmaxerr = VMaxfiterr))
    except KeyError:
        KMfit= VMaxfit = afit= KMfiterr= VMaxfiterr= afiterr = redchisqMM =  None

    try:
        popt, pcov = curve_fit(exp_fit, x, y)
        ax.plot(x, exp_fit(x, *popt), "g--", lw = 3)

        Vfit = popt[0]
        Vfiterr = np.sqrt(np.diag(pcov))[0]
        OD_mod = exp_fit(x, *popt)
        redchisqexp = redchisqg(y, OD_mod, deg = 3)

        if redchisqMM != None:
            if redchisqexp < redchisqMM:
                plt.text(0.8 * x[-1], np.mean(y) + 0.1, "$V_{max exp}$" + " = {Vmax:5.3f} +- {Vmaxerr:5.3f}  exp better".format(Vmax = Vfit,
                                                                                                   Vmaxerr = Vfiterr))
            else:
                plt.text(0.8 * x[-1], np.mean(y) + 0.1, "$V_{max exp}$" + " = {Vmax:5.3f} +- {Vmaxerr:5.3f}  MM better".format(Vmax = Vfit,
                                                                                                   Vmaxerr = Vfiterr))
        else:
            plt.text(0.8 * x[-1], np.mean(y) + 0.1, "$V_{max exp}$" + " = {Vmax:5.3f} +- {Vmaxerr:5.3f}".format(Vmax = Vfit, Vmaxerr = Vfiterr))

    except:
        Vfit = None
        Vfiterr = None
        redchisqexp = None

    #sort out misfitted
    if VMaxfit != None:
        if VMaxfiterr > 0.5 * VMaxfit:
            KMfit= VMaxfit = afit=  KMfiterr= VMaxfiterr= afiterr = redchisqMM =  None

    if Vfit != None:
        if Vfiterr > 0.5 * Vfit:
            Vfit = None
            Vfiterr = None
            redchisqexp = None


    if key != None:
        fitdict[key] = [KMfit,KMfiterr, VMaxfit, VMaxfiterr, afit,  afiterr, redchisqMM, Vfit, Vfiterr, redchisqexp]
        return fitdict


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

                fig = plt.figure()
                ax = plt.axes()
                simpleaxis(ax)


                y = thedict[key]
                ax.plot(x, y, "bo", ms=10)
                plt.title("OD600 of {well}".format(well = key + "_with:_" + coordtoindict[key]  + DATE))
                plt.xlabel("time in [min]")
                if KIND == "Nils_":
                    plt.ylabel("Optical Density at 600 nm")
                elif KIND == "Fluo_":
                    plt.ylabel("Fluorescence")
                #plt.yscale("log")

                plt.xlim((0, 180))
                if max(y) > UPPERLIMIT:
                    plt.ylim(ymin = LOWERLIMIT)
                else:
                    plt.ylim((LOWERLIMIT, UPPERLIMIT))

                if fitdict != None:


                    fitdict = my_fitting(x, y, fitdict, ax, key)
                    lg = None
                else:
                    lg = None

                if (not os.path.exists(FOLDER + "automated_plots")):
                    os.makedirs(FOLDER + "automated_plots")

                if key in IGNORELIST:
                    dateattach = DATE + "_ignore"
                else:
                    dateattach = DATE
                if lg == None:
                    plt.savefig(FOLDER + "automated_plots/plot_of_{well}.png".format(well = key + "_with_" +
                                                                                     coordtoindict[key]  + dateattach), dpi = 200)
                else:
                    plt.savefig(FOLDER + "automated_plots/plot_of_{well}.png".format(well = key + "_with_" +
                                                                                     coordtoindict[key]  + dateattach),
                                bbox_extra_artists=(lg,), bbox_inches='tight', dpi = 200)
                plt.close()
        if fitdict != None:
            return fitdict


    else:

        fig = plt.figure()
        ax = plt.axes()
        simpleaxis(ax)

        plotlist = plotlisttuple[0]
        maxcount = False

        x = thedict["time"]
        count = 0
        for key in plotlist:

            y = thedict[key]
            if max(y) > UPPERLIMIT:
                maxcount = True

            if count < 7:
                ax.plot(x, y, label = "{well}".format(well = key + "with" + coordtoindict[key]), lw = 3.)
            elif count < 14:
                ax.plot(x, y, "x",  label = "{well}".format(well = key + "with" + coordtoindict[key]), ms=10.)
            else:
                ax.plot(x, y, "o",  label = "{well}".format(well = key + "with" + coordtoindict[key]), ms=10.)
            count += 1


            if fitdict != None:
                blubb = my_fitting(x, y, fitdict, ax)
                blubb = None
        if maxcount:
            plt.ylim(ymin = LOWERLIMIT)
        else:
            plt.ylim((LOWERLIMIT, UPPERLIMIT))
        plt.xlim((0, 180))

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
    #global UPPERLIMIT
    #global LOWERLIMIT
    #global FOLDER

    '''
    datalist is a list of datatuples with mean values, errors and name in this sequence
    '''
    if len(datalist) > 1:
        fig = plt.figure()
        ax = plt.axes()
        simpleaxis(ax)

        maxcount = False

        x = timelist
        count = 0
        for tuplehere in datalist:
            y = tuplehere[0]
            if max(y) > UPPERLIMIT:
                maxcount = True


            if count < 7:
                ax.errorbar(x, y, elinewidth=1, yerr=tuplehere[1], label = "{well}".format(well = tuplehere[2]), lw = 3.)
            elif count < 14:
                ax.errorbar(x, y, elinewidth=1, fmt = "x", yerr=tuplehere[1], label = "{well}".format(well = tuplehere[2]), ms=10.)
            else:
                ax.errorbar(x, y, elinewidth=1, fmt = "o", yerr=tuplehere[1], label = "{well}".format(well = tuplehere[2]), ms=10.)
            count += 1
            #plt.errorbar(x, y, yerr=tuplehere[1], fmt = None)


            if fitdict != None:
                blubb = my_fitting(x, y, fitdict, ax)
                blubb = None
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
    fig = plt.figure()
    ax = plt.axes()
    simpleaxis(ax)

    ax.plot(datadict["time"], datadict["measuretemperature"], "r-")


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

    fig = plt.figure()
    ax = plt.axes()
    simpleaxis(ax)


    for lystype in lystypelist:
        x = []
        y = []
        yerr = []
        for key in dictoftoplottypes[lystype]:
            if key not in IGNORELIST:
                x.append(float(whatiswheredict["temperature"][key]))
                y.append(fitdict[key][7]) #7: Vfit (exp), 2: VMax (MM)
                yerr.append( fitdict[key][8])
        x  = np.array(x)
        y = np.array(y)
        yerr = np.array(yerr)

        keep = (y > 0) & (yerr > 0)
        x = x[keep]
        y = y[keep]
        yerr = yerr[keep]

        if np.size(y) > 0:

            ynormed = y / np.max(y)
            yerrnormed = y / np.max(y)


            if count < 7:
                ax.errorbar(x, y, yerr = yerr, fmt ="o", label = lystype, ms=10.)
            else:
                ax.errorbar(x, y, yerr = yerr, fmt ="x", label = lystype, ms=10.)
            count += 1

    plt.xlabel("temperature [°C]")
    plt.ylabel("activity [1/min]")



    lg = plt.legend(loc = 'upper right', bbox_to_anchor = (1.3, 1))
    if lg != None:
        lg.draw_frame(False)
    plt.savefig(FOLDER + "resultsplotlamlys.png", bbox_extra_artists=(lg,), bbox_inches='tight', dpi = 200)
    plt.savefig(RESULTFOLDER + "resultsplotlamlys" + DATE + ".png", bbox_extra_artists=(lg,), bbox_inches='tight', dpi = 200)
    plt.close()


def lysozyme_activity_plot_normed(dictoftoplottypes, whatiswheredict, fitdict, offsetactivity):

    '''
    generates a normed acitvity plot of the types, defined in dictoftoplottypes
    '''
    fig = plt.figure()
    ax = plt.axes()
    simpleaxis(ax)


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
                y.append(fitdict[key][7])  #7: Vfit (exp), 2: VMax (MM)
                yerr.append(fitdict[key][8])
        x  = np.array(x)
        y = np.array(y)
        yerr = np.array(yerr)

        keep = (y > 0.) & (yerr > 0.)
        x = x[keep]
        y = y[keep]
        yerr = yerr[keep]

        if np.size(y) > 0:
            y = y - offsetactivity
            y[y<0] = 0.
            sortarray = np.argsort(x)
            x = x[sortarray]
            y = y[sortarray]
            yerr = yerr[sortarray]


            # in smey... always all of the same type are collected, so that
            #they can be averaged afterwards. then they are passed to new... list
            sameys = []
            sameyerrs = []

            newylist = []
            newxlist = []
            newyerrlist = []
            for i in range(0,np.size(x)):
                if i == 0:
                    sameys.append(y[0])
                    sameyerrs.append(y[0])
                else:
                    if (x[i] == x[i-1]):
                        sameys.append(y[i])
                        sameyerrs.append(yerr[i])

                    elif (i != (np.size(x) - 1)):
                        newxlist.append(x[i-1])
                        sameys = np.array(sameys)
                        sameyerrs = np.array(sameyerrs)

                        newylist.append(np.mean(sameys))
                        newyerrlist.append( np.max([np.mean(  sameyerrs ) / np.sqrt(np.size(sameys)),
                                                    np.std(sameys)        / np.sqrt(np.size(sameys))]) )


                        sameys = [y[i]]
                        sameyerrs = [yerr[i]]


                    if (i == (np.size(x) - 1)):
                        newxlist.append(x[i-1])
                        sameys = np.array(sameys)
                        sameyerrs = np.array(sameyerrs)
                        newylist.append(np.mean(sameys))
                        #std and mean of err/n is not nice for both, so lets take maximum of it.
                        newyerrlist.append( np.max([np.mean(  sameyerrs ) / np.sqrt(np.size(sameys)),
                                                    np.std(sameys)        / np.sqrt(np.size(sameys))]) )


            newylist = np.array(newylist)
            newxlist = np.array(newxlist)
            newyerrlist = np.array(newyerrlist, dtype = float)
            if 37.0 in newxlist:
                refactivity = newylist[np.where(37.0 == newxlist)[0][0]]
                refactivityerr = newyerrlist[np.where(37.0 == newxlist)[0][0]]
                plt.ylabel("normed activity [activity of 37°C]")
                if refactivity == 0.:
                    refactivity = np.max(newylist)
                    refactivityerr = newyerrlist[np.argmax(newylist)]
                    plt.ylabel("normed activity [maximum activity]")
            else:
                refactivity = np.max(newylist)
                refactivityerr = newyerrlist[np.argmax(newylist)]
                plt.ylabel("normed activity [maximum activity]")

            ynormed = newylist / refactivity
            yerrnormed = (np.sqrt( (newyerrlist / newylist)**2 +
                                  ( refactivityerr / refactivity  )**2 ) * ynormed)





            if count < 7:

                ax.errorbar(newxlist, ynormed, yerr = yerrnormed, fmt="o", label = lystype, ms=15.)
            else:

                ax.errorbar(newxlist, ynormed, yerr = yerrnormed, fmt="x",label = lystype, ms=15.)
            count += 1
            plt.ylim(ymin = 0, ymax = 1.1)


    plt.xlabel("temperature [°C]")




    lg = plt.legend(loc = 'upper right', bbox_to_anchor = (1.3, 1))
    if lg != None:
        lg.draw_frame(False)
    plt.savefig(FOLDER + "resultsplotlamlysnormed.png", bbox_extra_artists=(lg,), bbox_inches='tight', dpi = 200)
    plt.savefig(RESULTFOLDER + "resultsplotlamlysnormed" + DATE + ".png", bbox_extra_artists=(lg,), bbox_inches='tight', dpi = 200)
    plt.close()
