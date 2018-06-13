#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import argparse
import h5py

# Import Bokeh plotting.
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, GMapOptions
from bokeh.plotting import gmap
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import HoverTool, TapTool
from bokeh.layouts import row, column, gridplot

import locale 
locale.setlocale(locale.LC_ALL, '') 

# My airline scraping
import scrape_airfares as scr

# USD to AUD.
exchange_rate = 1.31

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


    # Taken from
    # https://stackoverflow.com/questions/24180527/argparse-required-arguments-listed-under-optional-arguments
    # Normally `argparse` lists all arguments as 'optional'.  However some of
    # my arguments are required so this hack makes `parser.print_help()`
    # properly show that they are.

    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    optional.add_argument("-d", "--date", dest="date",
                          help="Date for the meeting. 'DD/MM/YYYY'",
                          type=str)

    optional.add_argument("-f", "--fname_in", dest="fname_in",
                          help="Filename for the HDF5 data file containing "
                          "the cities, the institutes at each city and the "
                          "groups at each institute. " 
                          "Default: './data/astro3d_data.hdf5'",
                          default="./data/astro3d_data.hdf5", type=str)

    args = parser.parse_args()
    args = vars(args)

    return args


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


def determine_fares(city, city_dest, date):

    airfares = scr.scrape_airfares(city, city_dest, date)
    
    num_flights = len(airfares)
    prices = []

    for trip_num in range(0, num_flights):
        if airfares[trip_num]["stops"] != "Nonstop":
            continue

        prices.append(float(airfares[trip_num]['ticket price'])*exchange_rate)

    print(airfares)
    return prices


def deal_with_airfares(args, data_file, cities):

    mean_cost = {}
    airfare_cost = {}

    for city in cities:
        mean_cost[city] = 0.0

    for city in cities:
        airfare_cost[city] = {}

        # We need to get the airfares from every combination of cities.
        for count, city_dest in enumerate(cities):
            if city_dest == city:  # Don't travel to itself!
                continue

            prices = determine_fares(city, city_dest, args["date"])
            mean_cost[city_dest] += np.mean(prices)* \
                                   data_file["Cities"][city].attrs["NumPeople"]
            airfare_cost[city][city_dest] = prices 

            print("{0} to {1} costs {2}".format(city, city_dest, prices))

    print("The cost to hold a meeting in each city is:")
    for city in mean_cost.keys():
        print("{0}: {1}".format(city, 
                                locale.currency(mean_cost[city]*exchange_rate,
                                                grouping=True)))

    return airfare_cost


def plot_cities(GMap, airfare_plots, args):
    """
    Plots the location of the cities the institutes belong to. 

    Parameters
    ----------

    GMap: Bokeh GMap (Google Map) Axis. 
        Map that we're plotting the data on top of.

    args: Dictionary.  Required.
        Dictionary of arguments from the ``argparse`` package. See function
        `parse_inputs()`.
        Dictionary is keyed by the argument name (e.g., args['fname_in']).
        Used to determine the data file containing the data we're using. 

    Returns
    ----------

    None.  The data is plotted onto the Google Map axis. 
    """

    # First open the file that has all the data we're plotting.
    data_file = h5py.File(args["fname_in"], "r")

    inst_name = []
    lon = [] 
    lat = []
    NumPeople = []  # Total number of people per institute.
    NumPeople_group = []  # Number of people per group within each institute
                          # (will be an array of dicts). 

    # We need to count manually (i.e. without `enumerate`) because some cities
    # have multiple institutes.
    count = 0

    # The group structure for `data_file` is first keyed by each city that
    # contains an institute.  Each institute then has an entry, with each group
    # then having an entry inside it.
    # E.g., data_file["Cities"]["Melbourne"]["Swinburne University of
    # Technology"]["CIs"].value would give the number of CIs at Swinburne.

    cities = data_file["Cities"].keys()

    for city in cities:
        for institute in data_file["Cities"][city].keys():

            inst_name.append(institute)
            lon.append(data_file["Cities"][city].attrs["Coords"][0])
            lat.append(data_file["Cities"][city].attrs["Coords"][1])
            NumPeople.append(data_file["Cities"][city][institute].attrs["NumPeople"])

            groups = data_file["Cities"][city][institute].keys()

            NumPeople_group.append({})

            for group in groups:
                NumPeople_group[count][group] = \
                data_file["Cities"][city][institute][group].value 

            count += 1 

    # If a date is passed at Runtime we want to determine the airfares at
    # the date.

    if len(cities) > 1 and args["date"]:
        airfare_cost = deal_with_airfares(args, data_file, cities)

        airfares = [[] for x in range(len(cities))]
        for count, city in enumerate(cities):
            for dest_city in cities:
                if dest_city == city:
                    airfares[count].append([])
                else:      
                    airfares[count].append(airfare_cost[city][dest_city])
            
    

    # Now that we've got the number of people within each institute, we need to
    # construct an array that holds the number of people within each group.
    # This needs to be an array because Bokeh only likes them.  The structure
    # of this will be:

    # total_NumPeople_group = [[AIs at SUT, AIs at UMelb, AIs at ANU,...,],
    #                          [CIs at SUT, CIs at UMelb, CIs at ANU,...,],
    #                          [etc...]]
    group_names = [x for x in NumPeople_group[0].keys()]
    total_NumPeople_group = [[] for x in range(len(group_names))]

    for count in range(len(inst_name)):
        for group_num, group in enumerate(NumPeople_group[count]): 
            total_NumPeople_group[group_num].append(NumPeople_group[count][group])

    # We need to feed a dictionary into Bokeh so it knows what to list when we
    # hover over each point.
    data = dict(x=lon,
                y=lat,
                institutes=inst_name,
                people=NumPeople,)

    # Now lets add each of the groups to this dictionary...
    for count, group in enumerate(group_names): 
        data[group] = total_NumPeople_group[count]

    if args["date"]:
        for city_count, city in enumerate(cities):
            airfares_to_show = []
            for dest_count, dest_city in enumerate(cities):
                if dest_city == city:
                    airfares_to_show.append(0.0)
                    continue
                airfares_this_city = airfares[city_count][dest_count]
                airfares_to_show.append(np.median(airfares_this_city))

                #plot3 = airfare_plots[dest_city].circle(range(len(airfares_this_city)),
                #                                        airfares_this_city, 
                #                                        color=colors[city_count]) 
            airfare_plots[city].vbar(x=list(cities), 
                                     top=airfares_to_show,
                                     width=0.5) 

            airfare_plots[city].yaxis.axis_label = "Median Price"

            #data[city] = airfares_to_show 

    # Then turn it into a Bokeh friendly format.
    source = ColumnDataSource(data=data)

    # Plot a Cross at each of the capital cities.
    # Note: For places such as Melbourne that have multiple institutes, we
    # actually plot two Crosses but they're at the exact same lat/long.
    plot1 = GMap.cross('x', 'y', size=20, source=source, angle=45, line_width=5)

    # Then generate the tooltips that will be shown when the user hovers over a
    # point.
    tooltips = [("Institute", "@institutes"),
                ("Number People", "@people")]

    # Finally need to append the composition of each group at each institute to
    # these tooltips.
    for group in group_names:
        tooltip_name = group
        tooltip_value = "@{0}".format(group)

        tooltips.append((tooltip_name, tooltip_value))

    # Then add them to the plot.  We explicitly only render the tooltips for
    # these crosses as we will have other objects on the same map but we don't
    # want the tooltips to show for them.
    GMap.add_tools(HoverTool(renderers=[plot1], tooltips=tooltips))
 
    data_file.close()


def plot_group_means(GMap, args):
    """
    Plots the mean location of the groups. 

    Parameters
    ----------

    GMap: Bokeh GMap (Google Map) Axis. 
        Map that we're plotting the data on top of.

    args: Dictionary.  Required.
        Dictionary of arguments from the ``argparse`` package. See function
        `parse_inputs()`.
        Dictionary is keyed by the argument name (e.g., args['fname_in']).
        Used to determine the data file containing the data we're using. 

    Returns
    ----------

    None.  The data is plotted onto the Google Map axis. 
    """

    data_file = h5py.File(args["fname_in"],"r")

    group_weighted_lon = {} 
    group_weighted_lat = {}
    group_names = []

    total_weighted_lon = 0.0
    total_weighted_lat = 0.0

    NumPeople = {} 

    for city_count, city in enumerate(data_file["Cities"].keys()): 
        for institute in data_file["Cities"][city].keys():
            lon = data_file["Cities"][city][institute].attrs["Coords"][0]
            lat = data_file["Cities"][city][institute].attrs["Coords"][1]

            total_weighted_lon += lon * \
                                  data_file["Cities"][city][institute].attrs['NumPeople']
           
            total_weighted_lat += lat * \
                                  data_file["Cities"][city][institute].attrs['NumPeople']

            groups = data_file["Cities"][city][institute].keys()
            for group in groups:
                if city_count == 0:
                    group_weighted_lon[group] = 0.0
                    group_weighted_lat[group] = 0.0
                    NumPeople[group] = 0.0

                group_weighted_lon[group] += \
                        data_file["Cities"][city][institute][group].value * lon 

                group_weighted_lat[group] += \
                        data_file["Cities"][city][institute][group].value * lat 

                NumPeople[group] += \
                        data_file["Cities"][city][institute][group].value 


    for group in group_weighted_lon.keys():
        group_weighted_lon[group] /= NumPeople[group]
        group_weighted_lat[group] /= NumPeople[group]
        group_names.append(group)

    lon_values = [lon for lon in group_weighted_lon.values()]
    lat_values = [lat for lat in group_weighted_lat.values()]
    people = [num for num in NumPeople.values()]

    source = ColumnDataSource(data=dict(
                              x=lon_values,
                              y=lat_values,
                              group_name=group_names,
                              people=people,))

    plot2 = GMap.circle('x', 'y', size=15, source=source) 
    GMap.add_tools(HoverTool(renderers=[plot2], tooltips=[
                      ("Group", "@group_name"),
                      ("Number People", "@people")]))
   

    data_file.close()


def determine_cities(args):


    city_names = []
    with h5py.File(args["fname_in"], "r") as data_file:
   
        cities = data_file["Cities"].keys()
        for city in cities:
            city_names.append(city)
    return city_names 


def plot_data(args): 
    """
    Plots the mean location of the groups specified by the user.

    Parameters
    ----------

    args: Dictionary.  Required.
        Dictionary of arguments from the ``argparse`` package. See function
        `parse_inputs()`.
        Dictionary is keyed by the argument name (e.g., args['fname_in']).
        Used to determine the data file containing the data we're using. 

    Returns
    ----------

    None.  The figure is saved as a html file as 'test.html'. 
    """

    output_file("test.html")

    # First let's get the properties of the map we're drawing. 
    map_options = get_Gmap_options()

    # Bokeh hooks into Google Maps which requires an API key.
    API_key = get_google_key()

    # Now let's plot Australia!
    GMap = gmap(API_key, map_options,
             title="Australia")
        
    if args["date"]:
        city_names = determine_cities(args)
        airfare_plots = {}

        for city in city_names: 
            airfare_plots[city] = figure(x_range=city_names, plot_width=400, 
                                         plot_height=400, tools="", 
                                         toolbar_location=None,
                                         title=city)
    else:
        airfare_plots = None

    # Plot the cities each institution belongs to.
    plot_cities(GMap, airfare_plots, args)

    # Then for each group, plot the mean location of the group.
    plot_group_means(GMap, args)

    if args["date"]:      
        grid = []
        for city in city_names: 
            grid.append(airfare_plots[city])

        my_grid = gridplot(grid, ncols=2, plot_width=250, plot_height=250)

        show(row(GMap, my_grid))
    else:
        print(GMap)
        show(GMap)

if __name__ == '__main__':

    args = parse_inputs()

    set_globalplot_properties()

    plot_data(args) 

