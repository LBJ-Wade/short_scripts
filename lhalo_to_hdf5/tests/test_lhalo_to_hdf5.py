#!/usr/bin/env python
from __future__ import print_function
import numpy as np
import argparse
import sys
import h5py
import os
import pytest

test_dir = os.path.dirname(os.path.realpath(__file__))
location = "{0}/../".format(test_dir)
sys.path.append(location)

import lhalo_to_hdf5 as converter 

root_snapshot = 63

def parse_inputs():
    """
    Parses the command line input arguments.

    If there has not been an input or output file specified we run with the
    default test data. 

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
                        help="Path to the input HDF5 data file. "
                        "Default: {0}/test.binary".format(test_dir),
                        default="{0}/test.binary".format(test_dir))
    parser.add_argument("-o", "--fname_out", dest="fname_out",
                        help="Path to the output HDF5 data file. "
                        "Default: {0}/test.hdf5".format(test_dir),
                        default="{0}/test.hdf5".format(test_dir))

    args = parser.parse_args()

    # We require an input file and an output one.
    if args.fname_in is None:
        args.fname_in = "./test.binary"
    if args.fname_out is None:
        args.fname_out = "./test.hdf5"

    print("Running the test using binary file {0}"
          .format(args.fname_in))
    print("")

    return vars(args)


def my_test_root(args):
    """
    Checks that the pointers of the root halo in each tree are correct.

    This ensures that the root halo: has no descendants, is at the root redshift, 
    has no NextProgenitors. 

    Parameters
    ----------

    args: Dictionary.
        Dictionary containing the argsion parameters specified at runtime.
        Used to get file name. 

    Returns
    ----------

    None. ``Pytest.fail()`` is invoked if the test fails.
    """

    with h5py.File(args["fname_out"], "r") as hdf5_file:
        for tree_key in hdf5_file.keys():
            if hdf5_file[tree_key]['Descendant'][0] != -1:
                print("For {0} the descendant of the first halo is {1}"
                      .format(tree_key, hdf5_file[tree_key]['Descendant'][0]))
                print("For LHaloTrees the first Halo MUST be the root halo and"
                      " have a descendant ID of -1.")

                cleanup(args)
                pytest.fail()

            if hdf5_file[tree_key]['SnapNum'][0] != root_snapshot:
                print("For {0} the snapshot number of the first halo is {1}"
                      .format(tree_key, hdf5_file[tree_key]['SnapNum'][0]))
                print("For LHaloTrees the first halo MUST be the root halo and"
                      " be at the root redshift.  For mini-millennium this is "
                      "snapshot number {0}".format(root_snapshot))

                cleanup(args)
                pytest.fail()

            '''
            This doesn't necessarily need to be true.
            if hdf5_file[tree_key]['FirstHaloInFOFgroup'][0] != 0:
                print("For {0} the FirstHaloInFOFgroup for the first halo is {1}"
                      .format(tree_key, 
                              hdf5_file[tree_key]['FirstHaloInFOFgroup'][0]))
                print("For LHaloTrees the first halo MUST be the root halo and"
                      " a main FOF halo.") 

                cleanup(args)
                pytest.fail()
            '''

            if hdf5_file[tree_key]['NextProgenitor'][0] != -1:
                print("For {0} the NextProgenitor of the first halo is {1}"
                      .format(tree_key, hdf5_file[tree_key]['Descendant'][0]))
                print("For LHaloTrees the first Halo MUST be the root halo and"
                      " have a NextProgenitor ID of -1.")

                cleanup(args)
                pytest.fail()


def cleanup(args):
    """
    Remove the output HDF5 data. 

    Parameters
    ----------

    args: Dictionary.
        Dictionary containing the argsion parameters specified at runtime.
        Used to get file names.

    Returns
    ----------

    None
    """

    os.remove(args["fname_out"])

def test_run():
    """
    Wrapper to run all the tests.

    Parameters
    ----------

    None.

    Returns
    ----------

    None.
    """

    args = parse_inputs()

    converter.convert_binary_to_hdf5(args)
   
    my_test_root(args)

    cleanup(args)
if __name__ == "__main__":

    test_run()
