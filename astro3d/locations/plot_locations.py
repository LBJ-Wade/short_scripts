#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import argparse

# Import Bokeh plotting.
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, GMapOptions
from bokeh.plotting import gmap
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import HoverTool


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
    #colors = ['r', 'b', 'g', 'c']
    colors = ['#7b3294','#a4225f', '#a6dba0', '#d7191c','#d01c8b','#a6611a']


def get_Gmap_options():
    """
    Generates the map options for the Google Map-Bokeh implentation. 

    Parameters
    ----------

    None. 

    Returns
    ----------

    map_options: Bokeh `GMapOptions` class.
        Options that define the Google Map region Bokeh will plot.
    """

    Australia_lat = -27.46749  # Coords the map is centred on.
    Australia_lon = 133.02809

    map_options = GMapOptions(lat=Australia_lat, lng=Australia_lon, 
                              map_type="roadmap", zoom=4)

    return map_options


def get_google_key(key_dir="."):
    """
    Grabs the Google Maps API key from a file.

    This is kept locally on my machine so I don't expose it on Github.

    Function assumes the key is kept in a file called 'keys.txt'.

    Parameters
    ----------

    key_dir: String. Optional, default "." 
        Directory that contains the file with key. 

    Returns
    ----------

    key: String. Required.
        The Google Maps API key.
    """
    
    fname = "{0}/keys.txt".format(key_dir)
   
    with open(fname, "r") as f:
        key = f.read()

    return key


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

    output_file("test.html")

    # First let's draw the map of Australia.

    map_options = get_Gmap_options()

    # Now we have Australia drawn, let's mark the 4 ASTRO3D Cities.
    city_lon = [144.96332, # Melbourne
                149.12807, # Canberra
                151.209900, # Sydney
                115.8614] # Perth

    city_lat = [-37.814, # Melbourne
                -35.28346, # Canberra
                -33.865143, # Sydney
                -31.95224] # Perth

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
    mean_x_array = []
    mean_y_array = []
    data_array = []
    tags = []
    my_colors = []
    for count, group in enumerate(data.keys()):

        weighted_lon = np.sum(np.array(data[group]) * np.array(uni_lon)) \
                       /sum(data[group])

        weighted_lat = np.sum(np.array(data[group]) * np.array(uni_lat)) \
                       /sum(data[group])

        total_weighted_lon.append(weighted_lon)
        total_weighted_lat.append(weighted_lat) 

        mean_x_array.append(weighted_lon)
        mean_y_array.append(weighted_lat)
        data_array.append(sum(data[group]))
        tags.append(group)
        my_colors.append(colors[count])

        print("For {0} mean longitude is {1} and latitude is {2}".format(group,
              weighted_lon, weighted_lat))

    # If we're plotting more than one group, plot the mean of the groups.
    if (len(data.keys()) > 1):
        print("The total mean longitude is {0} and latitude is {1}" \
              .format(np.mean(total_weighted_lon), np.mean(total_weighted_lat)))

        total_mean_x, total_mean_y = (np.mean(total_weighted_lon),
                                      np.mean(total_weighted_lat)) 

        mean_x_array.append(total_mean_x)
        mean_y_array.append(total_mean_y)
        data_array.append(sum(data_array))
        tags.append("Total")
        my_colors.append(colors[count])

    source = ColumnDataSource(data=dict(
                              x=mean_x_array,
                              y=mean_y_array,
                              numbers=data_array,
                              group_tags=tags,
                              color=my_colors))

    hover = HoverTool(tooltips=[
                      ("Group", "@group_tags"),
                      ("Number", "@numbers")])

    API_key = get_google_key()

    p = gmap(API_key, map_options,
             title="Australia", tools=[hover]) 
    
    p.circle('x', 'y', size=15, source=source, fill_color='color') 
    
    show(p) 

if __name__ == '__main__':

    args, data = parse_inputs()

    set_globalplot_properties()

    plot_locations(data) 

