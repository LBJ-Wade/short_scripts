#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import argparse
import os
import itertools
from scipy.integrate import quad

h = 0.681
OmegaM = 0.302
OmegaL= 0.698

def parse_inputs():
    """
    Parses the command line input arguments.

    If there has not been an input or output grid specified a ValueError will
    be raised.

    The only accepted arguments for `precision` is "float" or "double"; any
    other input (including no input at all) will raise a ValueError. 

    If the size of the input grid is less than the size of the output grid a
    ValueError will be raised. This is a subsampler.

    If the size of the output grid is not a multiple of the input grid a
    ValueError will be raised.

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

    parser.add_argument("-f", "--camb_in", dest="camb_in",
                        help="Path to the input matter power spectrum from "
                        "CAMB. Required.")
    parser.add_argument("-z", "--redshift", dest="redshift",
                        help="Redshift we're calculating the power spectrum "
                        "for. Required.", type = float)
    parser.add_argument("-o", "--fname_out", dest="fname_out",
                        help="Path to the ouput file. Required.")

    args = parser.parse_args()

    # We require an input file and an output one.
    if args.camb_in is None or args.fname_out is None:
        print("Require an input power spectrum and output file.") 
        parser.print_help()
        raise ValueError 

    if args.redshift is None:
        print("Require a redshift to calculate the power spectrum at.")
        parser.print_help()
        raise ValueError 

    # Print some useful startup info. #
    print("")
    print("======================================")
    print("Input Power Spectrum: {0}".format(args.camb_in))
    print("Output File: {0}".format(args.fname_out))
    print("Redshift: {0}".format(args.redshift))
    print("======================================")
    print("")

    return vars(args)


def growth_int(z):
    return (1 + z) / pow(Hubble_z(h * 100, OmegaM, OmegaL, z), 3.0) 
          

def Hubble_z(Hubble0, OmegaM, OmegaL, z):

    return pow(Hubble0 *Hubble0 * (OmegaM * pow(1.0+z,3.0) + OmegaL), 0.5) 

def get_growth_factor(z):

    Hz = Hubble_z(h * 100.0, OmegaM, OmegaL, z)
    print(Hz)
    
    return growth(z) * Hz / (h * 100.0) / growth(0.0) 


def growth(z):

    growth_factor = quad(growth_int, z, np.inf)

    return growth_factor[0] 

def calculate_matter_power(args):

    k_power, pspec = np.loadtxt(args["camb_in"], unpack = True)     
    
    growth_factor = get_growth_factor(args["redshift"])
    print("Growth factor at {0} is {1}".format(args["redshift"],
                                               growth_factor))

    pspec_final = pspec * growth_factor 

    fname_kpower = "{0}_kbins".format(args["fname_out"])
    np.savez(fname_kpower, k_power)
    print("Successfully saved to {0}.npz".format(fname_kpower))

    fname_originalpspec = "{0}_originalpspec".format(args["fname_out"])
    np.savez(fname_originalpspec, pspec)
    print("Successfully saved to {0}.npz".format(fname_originalpspec))

    fname_pspec = "{0}_pspec".format(args["fname_out"])
    np.savez(fname_pspec, pspec_final)
    print("Successfully saved to {0}.npz".format(fname_pspec))

if __name__ == '__main__':

    args = parse_inputs()    
    calculate_matter_power(args) 
