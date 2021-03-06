# This Python file uses the following encoding: utf-8

import numpy as np
import matplotlib
matplotlib.use("GTK")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, fsolve
from scipy.special import lambertw
import os
from matplotlib import rc
from globals import *



matplotlib.rc("axes", titlesize = "Large", labelsize ="Large" )


def simpleaxis(ax):
    '''
    removes the upper and right axis from a plot
    '''

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()


def define_globals(date, folder, kind,  upperlimit, lowerlimit, legendplace,
                   ignorelist):
    global DATE
    global UPPERLIMIT
    global LOWERLIMIT
    global FOLDER
    global KIND
    global LEGENDPLACE
    global IGNORELIST
    global RESULTFOLDER
    global MATLABFOLDER

    MATLABFOLDER = "./matlabd2ddata/"
    RESULTFOLDER = "./only_resultplots/"
    UPPERLIMIT = upperlimit
    LOWERLIMIT = lowerlimit
    FOLDER = folder
    DATE = date
    KIND = kind
    LEGENDPLACE = legendplace
    IGNORELIST = ignorelist


def exp(x, A, lam, C):
    return A * np.exp(- lam * x) + C


def my_fitting(x, y, fitdict, ax, key=None, xyl=False):

    '''
    adds a fitted curve to the plot.
    returns a new fitdict, if key is set.
    '''
    fit = False
    if xyl:
        if (y[-1] - y[0] > 1000):
            fit = True
    else:
        if True:
            fit = True
    if fit:

        OD0 = y[0]
        # a = np.mean(y[-30:])
        if xyl:
            m = 1
            subtoP = np.mean(y[-5:])
        else:
            m = 1/1.160     # mg/ml

        def fitfunc(t, KM, VMax, a, slope):

            if (KM < 10) & (KM > 0) & (VMax > 0) & (VMax < 1):

                S0 = m * (OD0 - a)

                S = KM * np.real(lambertw((S0 / KM) *
                                  np.exp((S0 - (VMax * t)) / KM))) + slope * t
                OD = (S / m) + a

                return OD
            else:
                return 1e10

        def exp_fit(t, VMax, OD0, a, slope):
            return (OD0 - a) * np.exp(-VMax * t) + a + slope*t


        def fitfunc_xyl(t, KM, VMax, a, slope):

            if (KM < 100000) & (KM > 0) & (VMax > 0) & (VMax < 100000):

                P0 = m * (OD0 - a)

                P = subtoP * (1 - KM * np.real(lambertw((1 / KM) *
                           np.exp((1 - (VMax * t)) / KM)))) + P0
                OD = (P / m) + a

                return OD
            else:
                return 1e10

        def exp_fit_xyl(t, VMax, OD0, maxi):
            '''
            maxi is maximum of curve, a is fluorescence of empty well
            '''
            P0 = m * (OD0)
            Pmaxi = m * (maxi)

            P = - (Pmaxi - P0) * np.exp(-VMax * t) + Pmaxi
            return P/m



        # plt.plot(make_param(y[1:6], x[1:6], a, OD0), make_result(y[1:6], x[1:6], m, OD0), "bo")
        # plt.xlim(xmin = 0)
        # plt.ylim(ymin = 0)
        # the fitting
        try:
            if xyl:
                # noch Anfangsparameter setzen
                popt, pcov = curve_fit(fitfunc_xyl, x, y, p0 = (0.1, 0.1, y[0], -0.001))
            else:
                popt, pcov = curve_fit(fitfunc, x, y, p0 = (0.1, 0.1, y[-1], -0.001))

            KMfit, VMaxfit, afit, slopefit  =  popt
            KMfiterr, VMaxfiterr, afiterr, slopefiterr =  np.sqrt(np.diag(pcov))
            OD_mod = fitfunc(x, *popt)

            redchisqMM = redchisqg(y, OD_mod, deg = 3)
            ax.plot(x, fitfunc(x, *popt), "r--", lw = 3)

            #plt.plot(x, fitfunc(x, 0.05, np.min(y)), "y--", lw = 3)
            #plt.plot(x, fitfunc(x, KMfit-KMfiterr, VMaxfit - VMaxfiterr, afit - afiterr), "g--", lw = 3)
            #plt.plot(x, fitfunc(x, KMfit+KMfiterr, VMaxfit + VMaxfiterr, afit + afiterr), "g--", lw = 3)
            if xyl:
                plt.text(20, 5000, "$V_{max MM}$ " + " = {Vmax:5.3f} +- {Vmaxerr:5.3f}".format(Vmax = VMaxfit,
                                                                                               Vmaxerr = VMaxfiterr))
            else:
                plt.text(0.8 * x[-1], np.mean(y)-0.1, "$V_{max MM}$ " + " = {Vmax:5.3f} +- {Vmaxerr:5.3f}".format(Vmax = VMaxfit,
                                                                                               Vmaxerr = VMaxfiterr))
                plt.text(0.8 * x[-1], np.mean(y)-0.1, "$KM$" + " = {KM:5.3f} +- {KMerr:5.3f} mg/ml".format(KM = KMfit,
                                                                                                   KMerr = KMfiterr))
        except:
            KMfit= VMaxfit = afit= KMfiterr= VMaxfiterr= afiterr = redchisqMM =  None

        try:
            if xyl:
                popt, pcov = curve_fit(exp_fit_xyl, x, y, p0=(1,1,30000))
                ax.plot(x, exp_fit_xyl(x, *popt), "g--", lw = 3)
                OD_mod = exp_fit_xyl(x, *popt)
                plt.text(20, 6000, "$V_{max exp}$" + " = {Vmax:5.3f}".format(Vmax = popt[0]))

            else:
                popt, pcov = curve_fit(exp_fit, x, y)
                ax.plot(x, exp_fit(x, *popt), "g--", lw = 3)
                OD_mod = exp_fit(x, *popt)

            Vfit = popt[0]
            Vfiterr = np.sqrt(np.diag(pcov))[0]
            ODzerofit = popt[1]
            offsetfit = popt[2]
            slopeexpfit = popt[3]


            redchisqexp = redchisqg(y, OD_mod, deg = 3)

            if redchisqMM != None:
                if redchisqexp < redchisqMM:
                    if xyl:
                        plt.text(20, 6000, "$V_{max exp}$" + " = {Vmax:5.3f} +- {Vmaxerr:5.3f} exp better".format(Vmax = Vfit, Vmaxerr = Vfiterr))
                    else:
                        plt.text(0.8 * x[-1], np.mean(y) + 0.1, "$V_{max exp}$" + " = {Vmax:5.3f} +- {Vmaxerr:5.3f} exp better".format(Vmax = Vfit, Vmaxerr = Vfiterr))

                else:
                    if xyl:
                        plt.text(20, 6000, "$V_{max exp}$" + " = {Vmax:5.3f} +- {Vmaxerr:5.3f} MM better".format(Vmax = Vfit, Vmaxerr = Vfiterr))
                    else:
                        plt.text(0.8 * x[-1], np.mean(y) + 0.1, "$V_{max exp}$" + " = {Vmax:5.3f} +- {Vmaxerr:5.3f} MM better".format(Vmax = Vfit, Vmaxerr = Vfiterr))

            else:
                if xyl:
                    plt.text(20, 6000, "$V_{max exp}$" + " = {Vmax:5.3f} +- {Vmaxerr:5.3f}".format(Vmax = Vfit, Vmaxerr = Vfiterr))
                else:
                    plt.text(0.8 * x[-1], np.mean(y) + 0.1, "$V_{max exp}$" + " = {Vmax:5.3f} +- {Vmaxerr:5.3f}".format(Vmax = Vfit, Vmaxerr = Vfiterr))

        except:
            Vfit = None
            Vfiterr = None
            redchisqexp = None
            ODzerofit = None
            offsetfit = None
            slopeexpfit = None

        #sort out misfitted
        if VMaxfit != None:
            if VMaxfiterr > 0.5 * VMaxfit:
                KMfit= VMaxfit = afit=  KMfiterr= VMaxfiterr= afiterr = redchisqMM =  None

        if Vfit != None:
            if Vfiterr > 0.5 * Vfit:
                Vfit = None
                Vfiterr = None
                redchisqexp = None
                ODzerofit = None
                offsetfit = None
                slopeexpfit = None
    else:
        Vfit = None
        Vfiterr = None
        redchisqexp = None
        ODzerofit = None
        offsetfit = None
        slopeexpfit = None
        KMfit= VMaxfit = afit=  KMfiterr= VMaxfiterr= afiterr = redchisqMM =  None

    if key != None:
        fitdict[key] = [KMfit,KMfiterr, VMaxfit, VMaxfiterr, afit,  afiterr,
                        redchisqMM, Vfit, Vfiterr, redchisqexp,
                        ODzerofit, offsetfit, slopeexpfit]
        return fitdict


def make_plots(thedict, coordtoindict, plotlisttuple = None, fitdict = None, xyl=False):
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
                if xyl:
                    plt.title("Fluo of {well}".format(well = key + "_with:_" + coordtoindict[key]  + DATE))
                else:
                    plt.title("OD600 of {well}".format(well = key + "_with:_" + coordtoindict[key]  + DATE))
                plt.xlabel("time in [min]")
                if KIND == "Nils_":
                    plt.ylabel("Optical Density at 600 nm")
                elif KIND == "Fluo_":
                    plt.ylabel("Fluorescence")
                elif KIND == "Charlotte_":
                    plt.ylabel("Fluorescence")
                #plt.yscale("log")

                plt.xlim((0, x[-1]))
                if max(y) > UPPERLIMIT:
                    plt.ylim(ymin = LOWERLIMIT)
                else:
                    plt.ylim((LOWERLIMIT, UPPERLIMIT))

                if fitdict != None:

                    fitdict = my_fitting(x, y, fitdict, ax, key, xyl=xyl)
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
                blubb = my_fitting(x, y, fitdict, ax, xyl=xyl)
                blubb = None
        if maxcount:
            plt.ylim(ymin = LOWERLIMIT)
        else:
            plt.ylim((LOWERLIMIT, UPPERLIMIT))
        plt.xlim((0, x[-1]))

        plt.title("{well}".format(well = plotlisttuple[1]))
        plt.xlabel("time in [min]")
        if KIND == "Nils_":
            plt.ylabel("Optical Density at 600 nm")
        elif KIND == "Fluo_":
            plt.ylabel("Fluorescence")
        elif KIND == "Charlotte_":
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



def make_calibration_plot(datadict, xlength=12):
    datadict["calibration"] = np.array(datadict["calibration"], dtype=float)
    datadict["calibration"] = np.reshape(datadict["calibration"], (8, xlength))

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
                    if np.size(x) == 1:
                        newylist = sameys
                        newyerrlist = sameyerrs
                        newxlist.append(x[0])
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
            try:
                if np.max(ynormed) > maxynormed:
                    maxynormed = np.max(ynormed)
            except:
                maxynormed = np.max(ynormed)





            if count < 7:

                ax.errorbar(newxlist, ynormed, yerr = yerrnormed, fmt="o", label = lystype, ms=15.)
            else:

                ax.errorbar(newxlist, ynormed, yerr = yerrnormed, fmt="x",label = lystype, ms=15.)
            count += 1
    if maxynormed < 1.2:
        plt.ylim(ymin = 0, ymax = 1.2)
    else:
        plt.ylim(ymin = 0, ymax = maxynormed + 0.1)


    plt.xlabel("temperature [°C]")




    lg = plt.legend(loc = 'upper right', bbox_to_anchor = (1.3, 1))
    if lg != None:
        lg.draw_frame(False)
        plt.savefig(FOLDER + "resultsplotlamlysnormed.png", bbox_extra_artists=(lg,), bbox_inches='tight', dpi = 200)
        plt.savefig(RESULTFOLDER + "resultsplotlamlysnormed" + DATE + ".png", bbox_extra_artists=(lg,), bbox_inches='tight', dpi = 200)
    plt.close()














# Michaelis Menten with product inhibition and shift of measurementdata



def make_data_and_modelfiles(lystype, biolrepl, temperature,
                             techrepl, datadict, well, forscriptdict, calibdict,
                             injectdict, fitdict, welltot0dict):
    '''
    appends the data of the given inputs to the lystype_biolrepl_temp.csv file"

    uses the techrepl as experiment value.

    forscriptdict is a dict of all the species for the models. For each species
    there is a list of the technical replicates.
    '''

    uniquestring = lystype + "_" + str(biolrepl) + "_" + str(temperature)
    uniquestring = uniquestring.replace(".", "p")

    if not os.path.exists(MATLABFOLDER):
        os.mkdir(MATLABFOLDER)
    if not os.path.exists(MATLABFOLDER + "Data/"):
        os.mkdir(MATLABFOLDER + "Data/")

    filename = (MATLABFOLDER + "Data/" + uniquestring + ".csv")

    # make injectdict
    if fitdict[well][11] != None:
        Q = calibdict[well]
        a = fitdict[well][11]   # der offset
        A = fitdict[well][10] - fitdict[well][11] # der Unterschied zwischen Anf und Ende
        VMax = fitdict[well][7]    # der Exponent
        slope = fitdict[well][12]       # die Endsteigung

        def hereexp (t):
            return Q - (A * np.exp(-VMax * t) + a + slope*t)

        t0 = fsolve(hereexp, x0=-4)[0]
        print well, t0
        t0 = welltot0dict[well]
        print "newt0 " + str(t0)
    else:
        t0 = 0
        print well + " was not fitted correctly"
    # + because t0 is negatve
    injectdict[uniquestring + str(techrepl)] = str(15 + t0)


    f = open(filename, "a")
    if techrepl == 1:
        f.close()
        f = open(filename, "w")
        f.write("time,Temp,experiment,OD_%s\n" % uniquestring)


    for i in range(len(datadict["time"])):
        if i == 0:
            f.write("0,{temp},{techre},{OD}\n"
                .format(temp=str(temperature), techre=str(techrepl),
                        OD=str(calibdict[well])))
        f.write("{time},{temp},{techre},{OD}\n"
                .format(time=str(datadict["time"][i] - t0),
                        temp=str(temperature), techre=str(techrepl),
                        OD=str(datadict[well][i])))
    f.close()



    if techrepl == 1:
        create_data_def_file(lystype, biolrepl, temperature)
        create_model_file(lystype, biolrepl, temperature)
    try:
        if techrepl not in forscriptdict[uniquestring]:
            forscriptdict[uniquestring].append(techrepl)
    except KeyError:
        forscriptdict[uniquestring] = [techrepl]
    return forscriptdict, injectdict






# Michaelis Menten with product inhibition

def create_data_def_file(lystype, biolrepl, temperature):
    uniquestring = lystype + "_" + str(biolrepl) + "_" + str(temperature)
    uniquestring = uniquestring.replace(".", "p")
    f = open(MATLABFOLDER + "Data/" + uniquestring + ".def", "w")

    f.write('DESCRIPTION\n' +
            '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +

            ('PREDICTOR\n' +
            'time        T   min time    0   120\n\n' +

            'INPUTS\n\n' +

            'OBSERVABLES\n' +
            'OD_{uni}       C   au  conc.   0  0   "0.0831 ' +
            ' + 1.116 * Sub_{uni}" "A"\n\n' +

            'ERRORS\n' +
            'OD_{uni}         "sd_OD"\n\n' +

            'CONDITIONS\n\n' +

            'RANDOM\n' +
            'experiment    INDEPENDENT\n').format(uni=uniquestring))
    f.close()

def create_model_file(lystype, biolrepl, temperature):
    if not os.path.exists(MATLABFOLDER + "Models/"):
        os.mkdir(MATLABFOLDER + "Models/")
    tempp = str(temperature).replace(".", "p")
    uniquestring = lystype + "_" + str(biolrepl) + "_" + tempp

    f = open(MATLABFOLDER + "Models/model" + uniquestring + ".def", "w")
    if "circ" not in lystype:
        f.write('DESCRIPTION\n' +
                '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +

                ('PREDICTOR\n' +
                't               T   "min"     "time"   0   120\n\n' +

                'COMPARTMENTS\n\n' +

                'STATES\n' +
                '{Sub} C    au    conc. cell\n\n' +

                'INPUTS\n\n' +

                'ODES\n' +
                '" - ({kcat} * {Enz} * {Sub}) / ((1 + ({initSub} - {Sub})/{Ki}) * ({KM} + {Sub} + kdecay * {Sub}))"\n\n').format(
                        kcat="kcat_" + lystype, Enz="Enz_" + uniquestring,
                        Sub="Sub_" + uniquestring, KM="KM_" + lystype,
                        initSub="init_Sub_" + uniquestring, Ki="Ki_" + lystype) +


                'DERIVED\n\n' +

                'CONDITIONS\n')
        if str(temperature) != "37.0":
            f.write("Enz_" + uniquestring + "    Enz_" + lystype + "_" +
                    str(biolrepl) + "_37p0*act_"+ lystype + "_" + tempp + "\n")


    elif "circ" in lystype:
        f.write('DESCRIPTION\n' +
                '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +

                ('PREDICTOR\n' +
                't               T   "min"     "time"   0   120\n\n' +

                'COMPARTMENTS\n\n' +

                'STATES\n' +
                '{Sub} C    au    conc. cell\n\n' +

                'INPUTS\n\n' +

                'ODES\n' +
                '" - ({kcat} * {Enz} * {Sub}) / (((1 + ({initSub} - {Sub})/{Ki}) * {KM}) + {Sub}) + kdecay * {Sub}"\n\n').format(
                        kcat="kcat_" + lystype, Enz="Enz_" + uniquestring,
                        Sub="Sub_" + uniquestring, KM="KM_" + lystype,
                        initSub="init_Sub_" + uniquestring, Ki="Ki_" + lystype) +

                'DERIVED\n\n' +

                'CONDITIONS\n')

        if str(temperature) != "37.0":
            f.write("Enz_" + uniquestring + "    Enz_" + lystype + "_" +
                    str(biolrepl) + "_37p0*act_"+ lystype + "_" + tempp + "\n")
        f.write("kcat_" + lystype + "    kcat_linlys*kcatratio_" + lystype + "\n")
        f.write("KM_" + lystype + "    KM_linlys*KMratio_" + lystype + "\n")
        f.write("Ki_" + lystype + "    Ki_linlys*Kiratio_" + lystype + "\n")


def make_script_file(forscriptdict, coomassiedict, fixedconc):

    '''
    if fixconc, then all the enzyme concentrations will be set, or restrained
    '''

    f = open(MATLABFOLDER + "script.m", "w")

    f.write('clear;\n' +
            'arInit;\n')

    for uniquestring in forscriptdict:
        f.write("arLoadModel('%s');\n" % ("model" + uniquestring))
    f.write("\n")
    for uniquestring in forscriptdict:
        f.write("arLoadData('{data}','{model}','csv',true);\n".format(
                    data=uniquestring , model="model" + uniquestring))
    f.write("\n")
    f.write("arCompileAll;\n")
    f.write("\n")
    for uniquestring in forscriptdict:
        # for techrepl in forscriptdict[uniquestring]:
        #     f.write("arSetPars('offset_%s_experiment%s', 0.0831, 0, 0, -2, 2)\n"
        #             % (uniquestring, str(techrepl)))
        if "37p0" not in uniquestring:
            ly, biorepl, temp = uniquestring.split("_")
            f.write("arSetPars('act_" + ly + "_" temp + "', 0, 1, 1, -2, 1)\n\n")
    for lystype in coomassiedict:
        lys37 = lystype + "_37p0"
        if lys37 in forscriptdict:
            if "linlys_13" in lystype:
                if True:
                    f.write("arSetPars('Enz_%s', %s, 0, 0, 0, %s)\n" % (lys37,
                               str(coomassiedict[lystype][1]),
                               str(coomassiedict[lystype][1]  + 1   )))
            else:
                if fixedconc:
                    f.write("arSetPars('Enz_%s', %s, 0, 0, 0, %s)\n" % (lys37,
                               str(coomassiedict[lystype][0]),
                               str(coomassiedict[lystype][0] + 1)))
                lysn = lystype.split("_")[0]
                f.write("arSetPars('kcatratio_%s', 0, 0, 1, -2, 2)\n" % lysn)
                f.write("arSetPars('KMratio_%s', 0, 1, 1, -2, 2)\n" % lysn)
                f.write("arSetPars('Kiratio_%s', 0, 1, 1, -2, 2)\n" % lysn)
    f.write("\n")
    f.write("arFit;\n")












## Michaelis Menten with product inhibition and injection of stuff
#
#
#
#def create_data_def_file(lystype, biolrepl, temperature):
#    uniquestring = lystype + "_" + str(biolrepl) + "_" + str(temperature)
#    uniquestring = uniquestring.replace(".", "p")
#    f = open(MATLABFOLDER + "Data/" + uniquestring + ".def", "w")
#
#    f.write('DESCRIPTION\n' +
#            '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +
#
#            'PREDICTOR\n' +
#            'time        T   min time    0   130\n\n' +
#
#            'INPUTS\n\n' +
#
#            'OBSERVABLES\n' +
#            'OD_{uni}       C   au  conc.   0  0   "0.083 '.format(uni=uniquestring) +
#            ' + 1.116 * Sub_{uni}" "A"\n\n'.format(uni=uniquestring) +
#
#            'ERRORS\n' +
#            'OD_{temp}         "sd_OD_experiment"\n\n'.format(temp=uniquestring) +
#
#            'CONDITIONS\n\n' +
#
#            'RANDOM\n' +
#            'experiment    INDEPENDENT\n')
#    f.close()
#
#def create_model_file(lystype, biolrepl, temperature, techrepl):
#    if not os.path.exists(MATLABFOLDER + "Models/"):
#        os.mkdir(MATLABFOLDER + "Models/")
#    uniquestring = lystype + "_" + str(biolrepl) + "_" + str(temperature)
#    uniquestring = uniquestring.replace(".", "p")
#
#    f = open(MATLABFOLDER + "Models/model" + uniquestring + ".def", "w")
#    if "circ" not in lystype:
#        f.write('DESCRIPTION\n' +
#                '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +
#
#                ('PREDICTOR\n' +
#                't               T   "min"     "time"   0   130\n\n' +
#
#                'COMPARTMENTS\n\n' +
#
#                'STATES\n' +
#                '{Enz} C    au    conc. cell\n' +
#                '{Prod} C    au    conc. cell\n' +
#                '{EnzSub} C    au    conc. cell\n' +
#                '{EnzProd} C    au    conc. cell\n' +
#                '{Sub} C    au    conc. cell\n\n' +
#
#
#                'INPUTS\n' +
#
#                '{Inject}   C  nM  conc.  "{amnt_Enz} * (1/sqrt(2*pi*(0.1^2))) * exp(-(t - {t_inj})^2/(2*(0.1^2)))"  \n\n'.format(
#                                    Inject="Inject_" + uniquestring + "_experiment", amnt_Enz="amnt_Enz_" + uniquestring, t_inj = "t_inj_" + uniquestring + "_experiment")       +
#
#
#                'REACTIONS\n' +
#                '{Enz} + {Sub}    -> {EnzSub}         CUSTOM "{kbuild} * {Enz} * {Sub}"  \n' +
#                '{EnzSub}          -> {Enz} + {Sub}    CUSTOM "{kdis} * {EnzSub}"        \n' +
#                '{EnzSub}          -> {Enz} + {Prod}   CUSTOM "{kcat} * {EnzSub}"        \n' +
#                '{Enz} + {Prod}    -> {EnzProd}        CUSTOM "{kon} * {Enz} * {Prod}"   \n' +
#                '{EnzProd}         -> {Enz} + {Prod}   CUSTOM "{koff} * {Enz} * {Prod}"  \n' +
#                '{Sub}             ->                  CUSTOM "{kdecay} * {Sub}"         \n' +
#                '                  -> {Enz}            CUSTOM "{Inject}"                 \n' ).format(
#                        Enz="Enz_" + uniquestring, Sub="Sub_" + uniquestring,
#                        EnzSub="EnzSub_" + uniquestring, Prod="Prod_" + uniquestring ,
#                        EnzProd="EnzProd_" + uniquestring, Inject="Inject_" + uniquestring + "_experiment",
#                        kbuild="kbuild_" + lystype, kdis="kdis_" + lystype,
#                        kcat="kcat_" + lystype, kon="kon_" + lystype,
#                        koff="koff_" + lystype, kdecay="kdecay") +
#
#
#                'DERIVED\n\n' +
#
#                'CONDITIONS\n')
#        if str(temperature) != "37.0":
#            f.write("Enz_" + uniquestring + '    Enz_' + lystype + "_" +
#                    str(biolrepl) + "_37p0*act_"+ uniquestring + '\n')
#
#        f.write('init_Enz_'    + uniquestring +  '   "0"\n')
#        f.write('init_EnzSub_' + uniquestring +  '   "0"\n')
#        f.write('init_EnzProd_' + uniquestring + '   "0"\n')
#        f.write('init_EnzSub_' + uniquestring +  '   "0"\n')
#        f.write('init_Prod_' + uniquestring +    '   "0"\n')
#
#
#    elif "circ" in lystype:
#        f.write('DESCRIPTION\n' +
#                '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +
#
#                ('PREDICTOR\n' +
#                't               T   "min"     "time"   0   130\n\n' +
#
#                'COMPARTMENTS\n\n' +
#
#                'STATES\n' +
#                '{Enz}      C    au    conc. cell\n' +
#                '{Prod}     C    au    conc. cell\n' +
#                '{EnzSub}   C    au    conc. cell\n' +
#                '{EnzProd}  C    au    conc. cell\n' +
#                '{Sub}      C    au    conc. cell\n\n' +
#
#
#                'INPUTS\n' +
#
#                '{Inject}   C  nM  conc.  "{amnt_Enz} * (1/sqrt(2*pi*(0.1^2))) * exp(-(t - {t_inj})^2/(2*(0.1^2)))"  \n\n'.format(
#                                    Inject="Inject_" + uniquestring + "_experiment", amnt_Enz="amnt_Enz_" + uniquestring, t_inj = "t_inj_" + uniquestring + "_experiment" )       +
#
#
#                'REACTIONS\n' +
#                '{Enz} + {Sub}    -> {EnzSub}         CUSTOM "{kbuild} * {Enz} * {Sub}"  \n' +
#                '{EnzSub}          -> {Enz} + {Sub}    CUSTOM "{kdis} * {EnzSub}"        \n' +
#                '{EnzSub}          -> {Enz} + {Prod}   CUSTOM "{kcat} * {EnzSub}"        \n' +
#                '{Enz} + {Prod}    -> {EnzProd}        CUSTOM "{kon} * {Enz} * {Prod}"   \n' +
#                '{EnzProd}         -> {Enz} + {Prod}   CUSTOM "{koff} * {Enz} * {Prod}"  \n' +
#                '{Sub}             ->                  CUSTOM "{kdecay} * {Sub}"         \n' +
#                '                  -> {Enz}            CUSTOM "{Inject}"                 \n' ).format(
#                        Enz="Enz_" + uniquestring, Sub="Sub_" + uniquestring,
#                        EnzSub="EnzSub_" + uniquestring , Prod="Prod_" + uniquestring,
#                        EnzProd="EnzProd_" + uniquestring, Inject="Inject_" + uniquestring,
#                        kbuild="kbuild_" + lystype, kdis="kdis_" + lystype,
#                        kcat="kcat_" + lystype, kon="kon_" + lystype,
#                        koff="koff_" + lystype, kdecay="kdecay") +
#
#                'DERIVED\n\n' +
#
#                'CONDITIONS\n')
#
#        if str(temperature) != "37.0":
#            f.write('amnt_Enz_' + uniquestring + '    amnt_Enz_' + lystype + "_" +
#                    str(biolrepl) + "_37p0*act_"+ uniquestring + '\n')
#
#        f.write('init_Enz_'    + uniquestring +  '   "0"\n')
#        f.write('init_EnzSub_' + uniquestring +  '   "0"\n')
#        f.write('init_EnzProd_' + uniquestring + '   "0"\n')
#        f.write('init_EnzSub_' + uniquestring +  '   "0"\n')
#        f.write('init_Prod_' + uniquestring +    '   "0"\n')
#        # f.write("kcat_" + lystype + "    kcat_linlys*kcatratio_" + lystype + "\n")
#        # f.write("KM_" + lystype + "    KM_linlys*KMratio_" + lystype + "\n")
#
#
#
#def make_data_and_modelfiles(lystype, biolrepl, temperature,
#                             techrepl, datadict, well, forscriptdict, calibdict,
#                             injectdict, fitdict):
#    '''
#    appends the data of the given inputs to the lystype_biolrepl_temp.csv file"
#
#    uses the techrepl as experiment value.
#
#    forscriptdict is a dict of all the species for the models. For each species
#    there is a list of the technical replicates.
#    '''
#
#    uniquestring = lystype + "_" + str(biolrepl) + "_" + str(temperature)
#    uniquestring = uniquestring.replace(".", "p")
#
#    if not os.path.exists(MATLABFOLDER):
#        os.mkdir(MATLABFOLDER)
#    if not os.path.exists(MATLABFOLDER + "Data/"):
#        os.mkdir(MATLABFOLDER + "Data/")
#
#    filename = (MATLABFOLDER + "Data/" + uniquestring + ".csv")
#
#    f = open(filename, "a")
#    if techrepl == 1:
#        f.close()
#        f = open(filename, "w")
#        f.write("time,Temp,experiment,OD_%s\n" % uniquestring)
#
#
#    for i in range(len(datadict["time"])):
#        if i == 0:
#            f.write("0,{temp},{techre},{OD}\n"
#                .format(temp=str(temperature), techre=str(techrepl),
#                        OD=str(calibdict[well])))
#        f.write("{time},{temp},{techre},{OD}\n"
#                .format(time=str(datadict["time"][i] + 15),
#                        temp=str(temperature), techre=str(techrepl),
#                        OD=str(datadict[well][i])))
#    f.close()
#
#    # make injectdict
#    if fitdict[well][11] != None:
#        Q = calibdict[well]
#        c = fitdict[well][11]
#        A = fitdict[well][10] - fitdict[well][11]
#        alpha = fitdict[well][7]
#        t0 = - np.log((Q-c) / A) / alpha
#    else:
#        t0 = 0
#        print well + " was not fitted correctly"
#    # + because t0 is negatve
#    injectdict[uniquestring + str(techrepl)] = str(15 + t0)
#
#    if techrepl == 1:
#        create_data_def_file(lystype, biolrepl, temperature)
#        create_model_file(lystype, biolrepl, temperature, techrepl)
#    try:
#        if techrepl not in forscriptdict[uniquestring]:
#            forscriptdict[uniquestring].append(techrepl)
#    except KeyError:
#        forscriptdict[uniquestring] = [techrepl]
#    return forscriptdict, injectdict
#
#
#
#
#
#
#
#def make_script_file(forscriptdict, coomassiedict, fixedconc, injectdict=None):
#
#    '''
#    if fixconc, then all the enzyme concentrations will be set, or restrained
#    '''
#
#    f = open(MATLABFOLDER + "script.m", "w")
#
#    f.write('clear;\n' +
#            'arInit;\n')
#
#    for uniquestring in forscriptdict:
#        f.write("arLoadModel('%s');\n" % ("model" + uniquestring))
#    f.write("\n")
#    for uniquestring in forscriptdict:
#        f.write("arLoadData('{data}','{model}','csv',true);\n".format(
#                    data=uniquestring , model="model" + uniquestring))
#    f.write("\n")
#    f.write("arCompileAll;\n")
#    f.write("\n")
#    for uniquestring in forscriptdict:
#        for techrepl in forscriptdict[uniquestring]:
#            if injectdict is not None:
#                f.write("arSetPars('t_inj_%s_experiment%s', %s, 0, 0, -2, 20)\n"
#                       % (uniquestring, str(techrepl),
#                          injectdict[uniquestring+str(techrepl)]))
##             f.write("arSetPars('offset_%s_experiment%s', 0.0831, 0, 0, -2, 2)\n"
##                    % (uniquestring, str(techrepl)))
#        if "37p0" not in uniquestring:
#            f.write("arSetPars('act_" + uniquestring + "', 0, 1, 1, -2, 1)\n\n")
#    f.write("arSetPars('kdecay" + "', -3, 1, 1, -5, 0)\n\n")

#    for lystype in coomassiedict:
#        lys37 = lystype + "_37p0"
#        if lys37 in forscriptdict:
#            if "linlys" in lystype:
#                if fixedconc:
#                    f.write("arSetPars('Enz_%s', %s, 0, 0, 0, %s)\n" % (lys37,
#                               str(coomassiedict[lystype][1]),
#                               str(coomassiedict[lystype][1] + 1)))
#            else:
#                if fixedconc:
#                    f.write("arSetPars('Enz_%s', %s, 0, 0, 0, %s)\n" % (lys37,
#                               str(coomassiedict[lystype][0]),
#                               str(coomassiedict[lystype][0] + 1)))
#                lysn = lystype.split("_")[0]
#                # f.write("arSetPars('kcatratio_%s', 0, 1, 1, -2, 2)\n" % lysn)
#                # f.write("arSetPars('KMratio_%s', 0, 1, 1, -2, 2)\n" % lysn)
#    f.write("\n")
#    f.write("arFit;\n")



























# mm ODE


#def make_data_and_modelfiles(lystype, biolrepl, temperature,
#                             techrepl, datadict, well, forscriptdict):
#    '''
#    appends the data of the given inputs to the lystype_biolrepl_temp.csv file"
#
#    uses the techrepl as experiment value.
#
#    forscriptdict is a dict of all the species for the models. For each species
#    there is a list of the technical replicates.
#    '''
#
#    uniquestring = lystype + "_" + str(biolrepl) + "_" + str(temperature)
#    uniquestring = uniquestring.replace(".", "p")
#
#    if not os.path.exists(MATLABFOLDER):
#        os.mkdir(MATLABFOLDER)
#    if not os.path.exists(MATLABFOLDER + "Data/"):
#        os.mkdir(MATLABFOLDER + "Data/")
#
#    filename = (MATLABFOLDER + "Data/" + uniquestring + ".csv")
#
#    f = open(filename, "a")
#    if techrepl == 1:
#        f.close()
#        f = open(filename, "w")
#        f.write("time,Temp,experiment,OD_%s\n" % uniquestring)
#
#    for i in range(len(datadict["time"])):
#        f.write("{time},{temp},{techre},{OD}\n"
#                .format(time=str(datadict["time"][i]),
#                        temp=str(temperature), techre=str(techrepl),
#                        OD=str(datadict[well][i])))
#    f.close()
#
#    if techrepl == 1:
#        create_data_def_file(lystype, biolrepl, temperature)
#        create_model_file(lystype, biolrepl, temperature)
#    try:
#        forscriptdict[uniquestring].append(techrepl)
#    except KeyError:
#        forscriptdict[uniquestring] = [techrepl]
#    return forscriptdict
#
#
#def create_data_def_file(lystype, biolrepl, temperature):
#    uniquestring = lystype + "_" + str(biolrepl) + "_" + str(temperature)
#    uniquestring = uniquestring.replace(".", "p")
#    f = open(MATLABFOLDER + "Data/" + uniquestring + ".def", "w")
#
#    f.write('DESCRIPTION\n' +
#            '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +
#
#            'PREDICTOR\n' +
#            'time        T   min time    0   105\n\n' +
#
#            'INPUTS\n\n' +
#
#            'OBSERVABLES\n' +
#            'OD_{uni}       C   au  conc.   0  0   "offset_{uni}_experiment '.format(uni=uniquestring) +
#            '- (dec_{uni}_experiment * t) + 1.116 * Sub_{uni}" "A"\n\n'.format(uni=uniquestring) +
#
#            'ERRORS\n' +
#            'OD_{temp}         "sd_OD"\n\n'.format(temp=uniquestring) +
#
#            'CONDITIONS\n\n' +
#
#            'RANDOM\n' +
#            'experiment    INDEPENDENT\n')
#    f.close()
#
#
## Michaelis Menten with product inhibition
#
#def create_data_def_file(lystype, biolrepl, temperature):
#    uniquestring = lystype + "_" + str(biolrepl) + "_" + str(temperature)
#    uniquestring = uniquestring.replace(".", "p")
#    f = open(MATLABFOLDER + "Data/" + uniquestring + ".def", "w")
#
#    f.write('DESCRIPTION\n' +
#            '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +
#
#            'PREDICTOR\n' +
#            'time        T   min time    0   105\n\n' +
#
#            'INPUTS\n\n' +
#
#            'OBSERVABLES\n' +
#            'OD_{uni}       C   au  conc.   0  0   "offset_{uni}_experiment '.format(uni=uniquestring) +
#            ' + 1.116 * Sub_{uni}" "A"\n\n'.format(uni=uniquestring) +
#
#            'ERRORS\n' +
#            'OD_{temp}         "sd_OD"\n\n'.format(temp=uniquestring) +
#
#            'CONDITIONS\n\n' +
#
#            'RANDOM\n' +
#            'experiment    INDEPENDENT\n')
#    f.close()
#
#def create_model_file(lystype, biolrepl, temperature):
#    if not os.path.exists(MATLABFOLDER + "Models/"):
#        os.mkdir(MATLABFOLDER + "Models/")
#    uniquestring = lystype + "_" + str(biolrepl) + "_" + str(temperature)
#    uniquestring = uniquestring.replace(".", "p")
#
#    f = open(MATLABFOLDER + "Models/model" + uniquestring + ".def", "w")
#    if "circ" not in lystype:
#        f.write('DESCRIPTION\n' +
#                '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +
#
#                'PREDICTOR\n' +
#                't               T   "min"     "time"   0   105\n\n' +
#
#                'COMPARTMENTS\n\n' +
#
#                'STATES\n' +
#                '{Sub} C    au    conc. cell\n\n'.format(Sub="Sub_" + uniquestring) +
#
#                'INPUTS\n\n' +
#
#                'ODES\n' +
#                '" - ({kcat} * {Enz} * {Sub}) / ((1 + ({initSub} - {Sub})/{Ki}) * ({KM} + {Sub} + kdecay * {Sub}))"\n\n'.format(
#                        kcat="kcat_" + lystype, Enz="Enz_" + uniquestring,
#                        Sub="Sub_" + uniquestring, KM="KM_" + lystype,
#                        initSub="init_Sub_" + uniquestring, Ki="Ki_" + lystype) +
#
#
#                'DERIVED\n\n' +
#
#                'CONDITIONS\n')
#        if str(temperature) != "37.0":
#            f.write("Enz_" + uniquestring + "    Enz_" + lystype + "_" +
#                    str(biolrepl) + "_37p0*act_"+ uniquestring + "\n")
#
#
#    elif "circ" in lystype:
#        f.write('DESCRIPTION\n' +
#                '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +
#
#                'PREDICTOR\n' +
#                't               T   "min"     "time"   0   105\n\n' +
#
#                'COMPARTMENTS\n\n' +
#
#                'STATES\n' +
#                '{Sub} C    au    conc. cell\n\n'.format(Sub="Sub_" + uniquestring) +
#
#                'INPUTS\n\n' +
#
#                'ODES\n' +
#                '" - ({kcat} * {Enz} * {Sub}) / (((1 + ({initSub} - {Sub})/{Ki}) * {KM}) + {Sub}) + kdecay * {Sub}"\n\n'.format(
#                        kcat="kcat_" + lystype, Enz="Enz_" + uniquestring,
#                        Sub="Sub_" + uniquestring, KM="KM_" + lystype,
#                        initSub="init_Sub_" + uniquestring, Ki="Ki_" + lystype) +
#
#                'DERIVED\n\n' +
#
#                'CONDITIONS\n')
#
#        if str(temperature) != "37.0":
#            f.write("Enz_" + uniquestring + "    Enz_" + lystype + "_" +
#                    str(biolrepl) + "_37p0*act_"+ uniquestring + "\n")
#        f.write("kcat_" + lystype + "    kcat_linlys*kcatratio_" + lystype + "\n")
#        f.write("KM_" + lystype + "    KM_linlys*KMratio_" + lystype + "\n")
#
#
#def make_script_file(forscriptdict, coomassiedict, fixedconc):
#
#    '''
#    if fixconc, then all the enzyme concentrations will be set, or restrained
#    '''
#
#    f = open(MATLABFOLDER + "script.m", "w")
#
#    f.write('clear;\n' +
#            'arInit;\n')
#
#    for uniquestring in forscriptdict:
#        f.write("arLoadModel('%s');\n" % ("model" + uniquestring))
#    f.write("\n")
#    for uniquestring in forscriptdict:
#        f.write("arLoadData('{data}','{model}','csv',true);\n".format(
#                    data=uniquestring , model="model" + uniquestring))
#    f.write("\n")
#    f.write("arCompileAll;\n")
#    f.write("\n")
#    for uniquestring in forscriptdict:
#        for techrepl in forscriptdict[uniquestring]:
#            f.write("arSetPars('offset_%s_experiment%s', 0.0831, 0, 0, -2, 2)\n"
#                    % (uniquestring, str(techrepl)))
#        if "37p0" not in uniquestring:
#            f.write("arSetPars('act_" + uniquestring + "', 0, 1, 1, -2, 1)\n\n")
#    for lystype in coomassiedict:
#        lys37 = lystype + "_37p0"
#        if lys37 in forscriptdict:
#            if "linlys" in lystype:
#                if fixedconc:
#                    f.write("arSetPars('Enz_%s', %s, 0, 0, 0, %s)\n" % (lys37,
#                               str(coomassiedict[lystype][1]),
#                               str(coomassiedict[lystype][1] + 1)))
#            else:
#                if fixedconc:
#                    f.write("arSetPars('Enz_%s', %s, 0, 0, 0, %s)\n" % (lys37,
#                               str(coomassiedict[lystype][0]),
#                               str(coomassiedict[lystype][0] + 1)))
#                lysn = lystype.split("_")[0]
#                f.write("arSetPars('kcatratio_%s', 0, 1, 1, -2, 2)\n" % lysn)
#                f.write("arSetPars('KMratio_%s', 0, 1, 1, -2, 2)\n" % lysn)
#    f.write("\n")
#    f.write("arFit;\n")
#



#Michaelis Menten, no product inhibition, fixed enzyme concentrations.
#
#def create_data_def_file(lystype, biolrepl, temperature):
#    uniquestring = lystype + "_" + str(biolrepl) + "_" + str(temperature)
#    uniquestring = uniquestring.replace(".", "p")
#    f = open(MATLABFOLDER + "Data/" + uniquestring + ".def", "w")
#
#    f.write('DESCRIPTION\n' +
#            '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +
#
#            'PREDICTOR\n' +
#            'time        T   min time    0   105\n\n' +
#
#            'INPUTS\n\n' +
#
#            'OBSERVABLES\n' +
#            'OD_{uni}       C   au  conc.   0  0   "offset_{uni}_experiment '.format(uni=uniquestring) +
#            '- (dec_{uni}_experiment * t) + 1.116 * Sub_{uni}" "A"\n\n'.format(uni=uniquestring) +
#
#            'ERRORS\n' +
#            'OD_{temp}         "sd_OD"\n\n'.format(temp=uniquestring) +
#
#            'CONDITIONS\n\n' +
#
#            'RANDOM\n' +
#            'experiment    INDEPENDENT\n')
#    f.close()
#
#def create_model_file(lystype, biolrepl, temperature):
#    if not os.path.exists(MATLABFOLDER + "Models/"):
#        os.mkdir(MATLABFOLDER + "Models/")
#    uniquestring = lystype + "_" + str(biolrepl) + "_" + str(temperature)
#    uniquestring = uniquestring.replace(".", "p")
#
#    f = open(MATLABFOLDER + "Models/model" + uniquestring + ".def", "w")
#    if "circ" not in lystype:
#        f.write('DESCRIPTION\n' +
#                '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +
#
#                'PREDICTOR\n' +
#                't               T   "min"     "time"   0   105\n\n' +
#
#                'COMPARTMENTS\n\n' +
#
#                'STATES\n' +
#                '{Sub} C    au    conc. cell\n\n'.format(Sub="Sub_" + uniquestring) +
#
#                'INPUTS\n\n' +
#
#                'ODES\n' +
#                '" - ({kcat} * {Enz} * {Sub}) / ({KM} + {Sub})"\n\n'.format(
#                            kcat="kcat_" + lystype, Enz="Enz_" + uniquestring,
#                            Sub="Sub_" + uniquestring, KM="KM_" + lystype) +
#
#                'DERIVED\n\n' +
#
#                'CONDITIONS\n')
#        if str(temperature) != "37.0":
#            f.write("Enz_" + uniquestring + "    Enz_" + lystype + "_" +
#                    str(biolrepl) + "_37p0*act_"+ uniquestring + "\n")
#
#
#    elif "circ" in lystype:
#        f.write('DESCRIPTION\n' +
#                '"' + lystype + " " + str(biolrepl) + " " + str(temperature) + '"\n\n' +
#
#                'PREDICTOR\n' +
#                't               T   "min"     "time"   0   105\n\n' +
#
#                'COMPARTMENTS\n\n' +
#
#                'STATES\n' +
#                '{Sub} C    au    conc. cell\n\n'.format(Sub="Sub_" + uniquestring) +
#
#                'INPUTS\n\n' +
#
#                'ODES\n' +
#                '" - ({kcat} * {Enz} * {Sub}) / ({KM} + {Sub})"\n\n'.format(
#                        kcat="kcat_" + lystype, Enz="Enz_" + uniquestring,
#                        Sub="Sub_" + uniquestring, KM="KM_" + lystype) +
#
#                'DERIVED\n\n' +
#
#                'CONDITIONS\n')
#
#        if str(temperature) != "37.0":
#            f.write("Enz_" + uniquestring + "    Enz_" + lystype + "_" +
#                    str(biolrepl) + "_37p0*act_"+ uniquestring + "\n")
#        f.write("kcat_" + lystype + "    kcat_linlys*kcatratio_" + lystype + "\n")
#        f.write("KM_" + lystype + "    KM_linlys*KMratio_" + lystype + "\n")
#
#
#def make_script_file(forscriptdict, coomassiedict, fixedconc):
#    '''
#    if fixconc, then all the enzyme concentrations will be set, or restrained
#    '''
#    f = open(MATLABFOLDER + "script.m", "w")
#
#    f.write('clear;\n' +
#            'arInit;\n')
#
#    for uniquestring in forscriptdict:
#        f.write("arLoadModel('%s');\n" % ("model" + uniquestring))
#    f.write("\n")
#    for uniquestring in forscriptdict:
#        f.write("arLoadData('{data}','{model}','csv',true);\n".format(
#                    data=uniquestring , model="model" + uniquestring))
#    f.write("\n")
#    f.write("arCompileAll;\n")
#    f.write("\n")
#    for uniquestring in forscriptdict:
#        for techrepl in forscriptdict[uniquestring]:
#            f.write("arSetPars('dec_%s_experiment%s', -3, 1, 1, -6, -2)\n"
#                    % (uniquestring, str(techrepl)))
#            f.write("arSetPars('offset_%s_experiment%s', -1, 1, 1, -2, 0)\n"
#                    % (uniquestring, str(techrepl)))
#        if "37p0" not in uniquestring:
#            f.write("arSetPars('act_" + uniquestring + "', 0, 1, 1, -2, 1)\n\n")
#    for lystype in coomassiedict:
#        lys37 = lystype + "_37p0"
#        if lys37 in forscriptdict:
#            if "linlys" in lystype:
#                if fixedconc:
#                    f.write("arSetPars('Enz_%s', %s, 0, 0, 0, %s)\n" % (lys37,
#                               str(coomassiedict[lystype][1]),
#                               str(coomassiedict[lystype][1] + 1)))
#            else:
#                if fixedconc:
#                    f.write("arSetPars('Enz_%s', %s, 0, 0, 0, %s)\n" % (lys37,
#                               str(coomassiedict[lystype][0]),
#                               str(coomassiedict[lystype][0] + 1)))
#                lysn = lystype.split("_")[0]
#                f.write("arSetPars('kcatratio_%s', 0, 1, 1, -2, 2)\n" % lysn)
#                f.write("arSetPars('KMratio_%s', 0, 1, 1, -2, 2)\n" % lysn)
#    f.write("\n")
#    f.write("arFit;\n")
#