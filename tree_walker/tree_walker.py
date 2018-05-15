#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import ytree
import argparse



def parse_inputs():
    """
    Parses the command line input arguments.

    If there has not been an input or output file specified a RuntimeError will
    be raised.

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

    parser.add_argument("-s", "--simulation", dest="simulation",
                        help="Name of the simulation to be visualized. "
                             "Required.")
    parser.add_argument("-f", "--fname", dest="treepath",
                        help="Path to one of the trees. Required")

    args = parser.parse_args()

    # We require an input file and an output one.
    if (args.simulation is None or args.treepath is None):
        parser.print_help()
        raise RuntimeError

    # Print some useful startup info. #
    print("")
    print("Running for simulation {0}".format(args.simulation))
    print("")

    return vars(args)


def set_parameters(simulation):

    if simulation == "Kali":
        Hubble_h = 0.681
        Omega_m = 0.302
        Omega_L = 0.698
        Omega_b = 0.0452
        BoxSize = 108.96 # Mpc/h
        Volume = BoxSize**3
        BaryonFrac = 0.17
        Y = 0.24   
        PartMass = 7.8436e6# Msun/h 
        a = np.loadtxt("/lustre/projects/p134_swin/jseiler/kali/a_list.txt")
    elif simulation == "Mini-Millennium":
        Hubble_h = 0.73
        Omega_m = 0.25
        Omega_L = 0.75
        Omega_b = 0.0
        BoxSize = 62.5 # Mpc/h

        a = np.loadtxt("/home/jseiler//sage/input/treefiles/millennium_mini/millennium.a_list")

    parameters = dict(HubbleParam=Hubble_h, Omega0=Omega_m, OmegaLambda=Omega_L,
                      BoxSize=BoxSize, PeriodicBoundariesOn=1, ComovingIntegrationOn=1,
                      UnitVelocity_in_cm_per_s=100000, UnitLength_in_cm=3.08568e+24,
                      UnitMass_in_g=1.989e+43)
    scale_factors = a

    return parameters, scale_factors
    

if __name__ == '__main__':

    args = parse_inputs()
    parameters, scale_factors = set_parameters(args["simulation"])  
    trees = ytree.load(args["treepath"],
                   parameters=parameters,
                   scale_factors=scale_factors)

    my_tree = trees[50] # Tree 0.
    w = np.where(my_tree["tree", "SnapNum"] == 50)[0]
    print("The FirstHaloInFOFgroup for halos at snapshot 50 are "
          "{0}".format(my_tree["tree", "FirstHaloInFOFgroup"][w]))
    print("The Descendants for halos at snapshot 50 are "
          "{0}".format(my_tree["tree", "Descendant"][w]))
    w_desc = my_tree["tree", "Descendant"][w] 
    print("The snapshot of the Descendants for halos at snapshot 50 are "
          "{0}".format(my_tree["tree", "SnapNum"][w_desc]))
    print("The Len for halos at snapshot 50 are "
          "{0}".format(my_tree["tree", "Len"][w]))
    #print(trees.field_info)
    #print(my_tree["tree", "SnapNum"])
