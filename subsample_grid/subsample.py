#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import h5py
from tqdm import tqdm
import argparse
import time
import os
from scipy import ndimage
import itertools

def parse_inputs():
    """
    Parses the command line input arguments.

    If there has not been an input or output grid specified a RuntimeError will
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

    parser.add_argument("-f", "--fname_in", dest="fname_in",
                        help="Path to the input grid file. Required.")
    parser.add_argument("-o", "--fname_out", dest="fname_out",
                        help="Path to the output grid file. Required.")
    parser.add_argument("-p", "--precision", dest="precision",
                        help="Precision for the grids. Accepted values are "
                             "'float' and 'double'. Required.")
    parser.add_argument("-s", "--gridsize_in", dest="gridsize_in",
                        help="Size of the grid (i.e., number of cells per "
                             "dimension) of input grid. Required.",
                        type = int)

    parser.add_argument("-d", "--gridsize_out", dest="gridsize_out",
                        help="Size of the grid (i.e., number of cells per "
                             "dimension) of output grid. Required.",
                        type=int)

    args = parser.parse_args()

    # We require an input file and an output one.
    if args.fname_in is None or args.fname_out is None:
        print("Both an input and output filepath is required.")
        parser.print_help()
        raise RuntimeError

    if args.precision == "float" or args.precision == "double":
        pass
    else: 
        print("The only accepted precision options are 'float' or 'double'.") 
        parser.print_help()
        raise RuntimeError

    if args.gridsize_in is None or args.gridsize_out is None:
        print("Both an input and ouput gridsize is required.")
        parser.print_help()
        raise RuntimeError

    # Print some useful startup info. #
    print("")
    print("The input grid file is {0}".format(args.fname_in))
    print("The output grid file is {0}".format(args.fname_out))
    print("The precision of the grids are {0}".format(args.precision))
    print("")

    return vars(args)


def read_grid(filepath, gridsize, precision):

    if precision == "float":
        byte_size = 4
    else:
        byte_size = 8

    filesize = os.stat(filepath).st_size
    if(pow(gridsize, 3.0) * byte_size != filesize):
        print("The size of the file is %d bytes whereas we expected it to be %d bytes" %(filesize, pow(gridsize, 3.0) * byte_size))
        raise ValueError

    fd = open(filepath, 'rb')
    grid = np.fromfile(fd, count = gridsize**3, dtype = precision)

    grid.shape = (gridsize, gridsize, gridsize)
    fd.close()

    return grid


def subsample_grid(args):

    conversion = int(args["gridsize_in"] / args["gridsize_out"])

    full_density = read_grid(args["fname_in"], args["gridsize_in"], 
                             args["precision"]) 

    footprint = np.ones((conversion, conversion, conversion))

    print("Input grid read, now convolving with the footprint.")
    # First generate a grid that contains the sliding sum of the original
    # density.
    new_density = ndimage.convolve(full_density, footprint, mode='wrap')  

    # Now since we want our new cells to be the discrete average (i.e., no
    # overlaps), we will only use every ``conversion`` cells.

    print("Convolution done, now reading the correct cells and normalizing.")
    final_new_density = np.zeros((args["gridsize_out"], args["gridsize_out"],
                                  args["gridsize_out"]))

    for (i, j, k) in itertools.product(range(args["gridsize_out"]),
                                       range(args["gridsize_out"]),
                                       range(args["gridsize_out"])): 
        final_new_density[i, j, k] = new_density[i * conversion, 
                                                 j * conversion, 
                                                 k * conversion] \
                                                / pow(conversion,3.0)

    
    final_new_density.tofile(args["fname_out"])
    print("Subsampled grid saved to {0}".format(args["fname_out"]))

   
if __name__ == '__main__':

    args = parse_inputs()    
    subsample_grid(args)
