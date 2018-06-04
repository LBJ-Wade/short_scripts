#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

if __name__ == '__main__':

    map = Basemap(projection='lcc',
                  width=4e6, height=4e6,
                  lat_0=-27.46749, lon_0=133.02809)
                  #lat_0=0.01, lon_0 =0.01)

    #Fill the globe with a blue color 
    map.drawstates(color='lightgray')
    #Fill the continents with the land color
    map.fillcontinents(color='lightgray')

    map.drawcoastlines()

    city_lon = [144.96332, # Melbourne
                149.12807, # Canberra
                151.209900, # Sydney
                115.8614] # Perth

    city_lat = [-37.814, # Melbourne
                -35.28346, # Canberra
                -33.865143, # Sydney
                -31.95224] # Perth

    city_x, city_y = map(city_lon, city_lat)

    map.scatter(city_x, city_y, marker='D', color='m', s = 50, 
                zorder=10)

    plt.savefig('test_.png')

