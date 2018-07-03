#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import csv
import argparse

def parse_inputs():
    """
    Parses the command line input arguments.

    If there has not been an input file specified a RuntimeError will be
    raised.

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
                        help="Path to the input csv data file. Required.")

    args = parser.parse_args()

    # We require an input file and an output one.
    if args.fname_in is None: 
        parser.print_help()
        raise RuntimeError

    # Print some useful startup info. #
    print("")
    print("The input CSV file is {0}".format(args.fname_in))
    print("")

    return vars(args)


def check_payments(args):
    """
    Checks how many students have registered and how many have paid.

    Parameters
    ----------

    args: Dictionary.  Required.
        Contains the runtime variables such as input file name.
        For full contents of the dictionary refer to ``parse_inputs``.

    Returns
    ----------

    None. The results will be printed to stdout.
    """

    name = []
    gender = []
    event = []
    email = []
    paid = []
    payID = []

    attending = 0
    has_paid = 0

    with open(args["fname_in"], 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            name.append(row[0])
            gender.append(row[1])
            event.append(row[2])
            email.append(row[3])
            paid.append(row[4])
            payID.append(row[5])
        
            if "HWSA" in row[2]:
                attending += 1
                if "True" in row[4]: 
                    has_paid += 1

    print("{0} people are attending Harley Wood and {1} have "
          "paid.".format(attending, has_paid))


if __name__ == '__main__':

    args = parse_inputs()
    check_payments(args)
