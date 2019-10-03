#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import h5py
from tqdm import tqdm
import argparse
import time


def get_LHalo_datastruct():
    """
    Generates the LHalo numpy structured array.

    Parameters
    ----------

    None.

    Returns
    ----------

    LHalo_Desc: numpy structured array.  Required.
        Structured array for the LHaloTree data format.
    """

    LHalo_Desc_full = [
        ('Descendant',          np.int32),
        ('FirstProgenitor',     np.int32),
        ('NextProgenitor',      np.int32),
        ('FirstHaloInFOFgroup', np.int32),
        ('NextHaloInFOFgroup',  np.int32),
        ('Len',                 np.int32),
        ('M_mean200',           np.float32),
        ('Mvir',                np.float32),
        ('M_TopHat',            np.float32),
        ('Pos',                 (np.float32, 3)),
        ('Vel',                 (np.float32, 3)),
        ('VelDisp',             np.float32),
        ('Vmax',                np.float32),
        ('Spin',                (np.float32, 3)),
        ('MostBoundID',         np.int64),
        ('SnapNum',             np.int32),
        ('FileNr',              np.int32),
        ('SubHaloIndex',        np.int32),
        ('SubHalfMass',         np.float32)
                         ]

    names = [LHalo_Desc_full[i][0] for i in range(len(LHalo_Desc_full))]
    formats = [LHalo_Desc_full[i][1] for i in range(len(LHalo_Desc_full))]
    LHalo_Desc = np.dtype({'names': names, 'formats': formats}, align=True)

    return LHalo_Desc


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

    parser.add_argument("-f", "--fname_in", dest="fname_in",
                        help="Path to the input HDF5 data file. Required.")
    parser.add_argument("-o", "--fname_out", dest="fname_out",
                        help="Path to the output HDF5 data file. Required.")

    args = parser.parse_args()

    # We require an input file and an output one.
    if (args.fname_in is None or args.fname_out is None):
        parser.print_help()
        raise RuntimeError

    # Print some useful startup info. #
    print("")
    print("The input LHaloTree binary file is {0}".format(args.fname_in))
    print("The output LHaloTree HDF5 file is {0}".format(args.fname_out))
    print("")

    return vars(args)


def convert_binary_to_hdf5(args):
    """
    Converts a binary LHaloTree to HDF5 format.

    The input LHaloTree binary file and output HDF5 file are specified at
    runtime and stored in the ``args`` Dictionary.

    Parameters
    ----------

    args: Dictionary.  Required.
        Contains the runtime variables such as input/output file names.
        For full contents of the dictionary refer to ``parse_inputs``.

    Returns
    ----------

    None
    """

    LHalo_Struct = get_LHalo_datastruct()

    with open(args["fname_in"], "rb") as binary_file, \
         h5py.File(args["fname_out"], "w") as hdf5_file:

        binary_file = open(args["fname_in"], "rb")

        # First get header info from the binary file.
        NTrees = np.fromfile(binary_file, np.dtype(np.int32), 1)[0]
        NHalos = np.fromfile(binary_file, np.dtype(np.int32), 1)[0]
        NHalosPerTree = np.fromfile(binary_file,
                                    np.dtype((np.int32, NTrees)), 1)[0]

        print("For file {0} there are {1} trees with {2} total halos"
              .format(args["fname_in"], NTrees, NHalos))

        # Write the header information to the HDF5 file.
        """
        hdf5_file.create_group("Header")
        hdf5_file["Header"].attrs.create("Ntrees", NTrees, dtype=np.int32)
        hdf5_file["Header"].attrs.create("totNHalos", NHalos, dtype=np.int32)
        hdf5_file["Header"].attrs.create("TreeNHalos", NHalosPerTree,
                                         dtype=np.int32)
        """
        # Now loop over each tree and write the information to the HDF5 file.
        for tree_idx in tqdm(range(NTrees)):
            binary_tree = np.fromfile(binary_file, LHalo_Struct,
                                      NHalosPerTree[tree_idx])

            for halo_idx in range(NHalosPerTree[tree_idx]):
                filenr = binary_tree["FileNr"][halo_idx]
                if filenr != 0:
                    print("Halo {0} FileNr {1}".format(halo_idx, filenr))

            """
            tree_name = "tree_{0:03d}".format(tree_idx)
            hdf5_file.create_group(tree_name)

            for subgroup_name in LHalo_Struct.names:
                hdf5_file[tree_name][subgroup_name] = binary_tree[subgroup_name]
            """

if __name__ == "__main__":

    args = parse_inputs()
    convert_binary_to_hdf5(args)
