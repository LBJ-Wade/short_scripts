#!/usr/bin:env python

import argparse
import h5py
import numpy as np


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

    parser.add_argument("-f", "--fname", dest="fname",
                        help="Name of the HDF5 file the data will be placed "
                        "in. Default: './data/astro3d_data.hdf5", 
                        default="./data/astro3d_data.hdf5", type=str)

    args = parser.parse_args()
    args = vars(args)

    print("Creating a HDF5 file called {0}".format(args["fname"]))

    return args


if __name__ == '__main__':

    args = parse_inputs()

    cities = ["Melbourne", "Canberra", "Sydney", "Perth"] 
    cities_coord = {"Melbourne":[144.96332,-37.814],
                    "Canberra":[149.12807,-35.28346],
                    "Sydney":[151.209900,-33.865143],
                    "Perth":[115.8614,-31.95224]}

    institutes = {"Melbourne":["Swinburne University of Technology",
                              "University of Melbourne"],
                 "Canberra": ["Australia National University"],
                 "Sydney":["University of Sydney"],
                 "Perth":["University of Western Australia",
                          "Curtin University"]}

    inst_coord = {"Swinburne University of "
                  "Technology":[145.0389546,-37.8221504],
                  "University of Melbourne":[144.9614,-37.7963],
                  "Australia National University":[149.11900,-35.28313],
                  "University of Sydney":[151.19037,-33.88915],
                  "University of Western "  
                  "Australia":[115.817830062,-31.974829434],
                  "Curtin University":[115.89405,-32.00469]}

    groups = ["CIs", "AIs", "Staff", "Students"]

    numbers = {"CIs":[3, 3, 3, 3, 2, 1],
               "AIs":[5, 3, 10, 6, 10, 3],
               "Staff":[3, 3, 5, 1, 3, 0],
               "Students":[7, 7, 11, 6, 7, 2]}

    inst_count = 0
    with h5py.File(args["fname"], "w") as f:
        for city in institutes.keys():
            numpeople_city = 0
            for institution in institutes[city]:
                NumPeople = 0
                for group in groups:
                    grp_name = "Cities/{0}/{1}/{2}/" \
                                .format(city, institution, group)

                    f.create_dataset(grp_name,
                                     data=np.array(numbers[group][inst_count]),
                                     dtype=np.int32)

                    print(numbers[group][inst_count])
                    NumPeople += numbers[group][inst_count]
                    numpeople_city += numbers[group][inst_count]

                grp_name = "Cities/{0}/{1}".format(city, institution)
                f[grp_name].attrs.create("Coords", inst_coord[institution])
                f[grp_name].attrs.create("NumPeople", NumPeople) 
                print("{0} people at {1}".format(NumPeople, institution))
                inst_count += 1
            grp_name = "Cities/{0}".format(city)
            f[grp_name].attrs.create("Coords", cities_coord[city])
            f[grp_name].attrs.create("NumPeople", numpeople_city) 

