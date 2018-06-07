#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import argparse


def parse_inputs():
    """
    Parses the command line input arguments.

    Parameters
    ----------

    None.

    Returns
    ----------

    args: Dictionary.  Required.
        Dictionary of arguments from the ``argparse`` package.
        Dictionary is keyed by the argument name (e.g., args['fname_in']).
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--CI", dest="do_CIs",
                        help="Flag to include CIs in calculation. Default: 1.",
                        default=1, type=int)

    parser.add_argument("-a", "--AI", dest="do_AIs",
                        help="Flag to include AIs in calculation. Default: 1.",
                        default=1, type=int)

    parser.add_argument("-f", "--staff", dest="do_staff",
                        help="Flag to include staff in calculation. Default: " 
                        "1.", default=1, type=int)

    parser.add_argument("-s", "--students", dest="do_students",
                        help="Flag to include students in calculation. " 
                        "Default: 1.", default=1, type=int)

    args = parser.parse_args()
    args = vars(args)

    if (args["do_students"] == 0 and args["do_CIs"] == 0 and args["do_AIs"] == 0
            and args["do_staff"] == 0):
        print("You've turned off flags for ALL of the ASTRO3D Members.")
        print("You must plot at least one of them!")
        raise RuntimeError

    # These are the number of people at each institute.
    # Order is: Swinburne, UniMelbourne, ANU, UniSydney, UniWA, Curtin.

    data = {}

    if (args["do_CIs"] == 1):

        CIs = [3,
               3,
               3,
               3,
               2,
               1]
        data["CIs"] = CIs

    if (args["do_AIs"] == 1):

        AIs = [5,
               3,
               10,
               6,
               10,
               3]
        data["AIs"] = AIs

    if (args["do_staff"] == 1):

        staff = [3,
                 3,
                 5,
                 1,
                 3,
                 0]

        data["Staff"] = staff 

    if (args["do_students"] == 1):

        students = [7,
                    7,
                    11,
                    6,
                    7,
                    2]
        data["Students"] = students

    return args, data


def set_globalplot_properties():
    """
    Sets parameters for plotting in this file. 

    Parameters
    ----------

    None.

    Returns
    ----------

    None.
    """

    global colors

    plt.rcdefaults()
    plt.rc('font', weight='bold')
    plt.rc('legend', numpoints=1, fontsize='x-large')
    plt.rc('text', usetex=True)
    colors = ['r', 'b', 'g', 'c']

def plot_locations(data): 
    """
    Plots the mean location of the groups specified by the user.

    Parameters
    ----------

    data: Dictionary, Required. 
        Contains the data for the groups the user wishes to plot.  
        Keyed by the name of the group.  Possible names are "CIs", "AIs",
        "Staff" and "Students".

    Returns
    ----------

    None.  The figure is saved in the directory as "test.png".
    """

    # First let's draw the map of Australia.
    Australia_lat = -27.46749  # These are the coords the map is centred on.
    Australia_lon = 133.02809

    map = Basemap(projection='lcc',
                  width=4e6, height=4e6,
                  lat_0=Australia_lat, lon_0=Australia_lon)

    map.drawstates(color='lightgray')
    map.drawstates(color='black')  # Draw state borders.
    map.fillcontinents(color='lightgray')
    map.drawcoastlines()

    # Now we have Australia drawn, let's mark the 4 ASTRO3D Cities.
    city_lon = [144.96332, # Melbourne
                149.12807, # Canberra
                151.209900, # Sydney
                115.8614] # Perth

    city_lat = [-37.814, # Melbourne
                -35.28346, # Canberra
                -33.865143, # Sydney
                -31.95224] # Perth

    city_x, city_y = map(city_lon, city_lat)

    map.scatter(city_x, city_y, marker='o', color='m', s = 50, 
                zorder=10, label = r"$\textbf{Lead Institutes}$")
    #plt.annotate(r'$\textbf{Melbourne}$', xy=(city_x[0], city_y[0]), xycoords='data',
    #             xytext=(-11, -15), textcoords='offset points',
    #             color='r')

    # Now it's time to calculate the means of the various groups.
    # Note: The exact coords of the Unis can differ very slightly, so define
    # them explicitly.
    uni_lon = [145.0389546,   # SUT.
               144.9614,      # UMelb.
               149.11900,     # ANU.
               151.19037,     # USyd.
               115.817830062, # UWA.
               115.89405]     # Curtin.

    uni_lat = [-37.8221504,   # SUT. 
               -37.7963,      # UMelb.
               -35.28313,     # ANU.
               -33.88915,     # USyd.
               -31.974829434, # UWA. 
               -32.00469]     # Curtin. 

    total_weighted_lon = []
    total_weighted_lat = [] 
    for count, group in enumerate(data.keys()):

        weighted_lon = np.sum(np.array(data[group]) * np.array(uni_lon)) \
                       /sum(data[group])

        weighted_lat = np.sum(np.array(data[group]) * np.array(uni_lat)) \
                       /sum(data[group])

        total_weighted_lon.append(weighted_lon)
        total_weighted_lat.append(weighted_lat) 

        mean_x, mean_y = map(weighted_lon, weighted_lat)

        label = r'$\textbf{' + group + r'}$'
        map.scatter(mean_x, mean_y, marker='o', 
                    color=colors[count], s = 50, zorder=10, label = label)

        print("For {0} mean longitude is {1} and latitude is {2}".format(group,
              weighted_lon, weighted_lat))

    # If we're plotting more than one group, plot the mean of the groups.     
    if (len(data.keys()) > 1):
        print("The total mean longitude is {0} and latitude is {1}" \
              .format(np.mean(total_weighted_lon), np.mean(total_weighted_lat)))

        total_mean_x, total_mean_y = map(np.mean(total_weighted_lon),
                                         np.mean(total_weighted_lat)) 

        label = r'$\textbf{' + group + r'}$'
        map.scatter(mean_x, mean_y, marker='o', 
                    color='k', s = 50, zorder=10, label = r"$\textbf{All}$")

    leg = plt.legend(loc='upper right', numpoints=1, labelspacing=0.1)
    for t in leg.get_texts():  # Reduce the size of the text
        t.set_fontsize(11)

    plt.savefig('test.png')

if __name__ == '__main__':

    args, data = parse_inputs()

    set_globalplot_properties()

    plot_locations(data) 

