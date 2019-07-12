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
    institution = []
    gender = []
    event = []
    email = []
    paid = []
    payID = []

    money = []
    isgoing = []

    attending = 0
    has_paid = 0

    print("")
    with open(args["fname_in"], 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            name.append(row[0])
            institution.append(row[1])
            gender.append(row[2])
            event.append(row[3])
            email.append(row[4])
            paid.append(row[6])
            payID.append(row[7])

            #if "Annual" in row[3] and "HWSA" not in row[3]:
            if "HWSA" in row[3]: 
                attending += 1
                isgoing.append(True)

                if "True" in row[6]: 
                    has_paid += 1
                    money.append(True)
                if "False" in row[6]:
                    #print("{0}: {1}".format(row[0], row[3]))
                    money.append(False)
            else:
                isgoing.append(False)
                money.append(False)

    w_isgoing = np.nonzero(isgoing)[0]
    w_paid = np.nonzero(money)[0]

    print("PEOPLE WHO HAVE PAID:")
    for w in w_paid:
        print("{0}: {1}".format(name[w], email[w]))

    print("")
    print("PEOPLE WHO HAVE NOT PAID:")
    print("")

    going_name = [] 
    going_institute = [] 
    going_email = []
    going_paid = []
    not_paid_email = []

    my_csv = open("./onlyASA.csv", "w")


    for w in w_isgoing:
        going_name.append(str(name[w]))
        going_email.append(str(email[w]))
        going_institute.append(str(institution[w]))
        going_paid.append(str(money[w]))
        row = "{0},{1},{2},{3}\n".format(name[w], institution[w], email[w],
                money[w]) 
        #my_csv.write(row)
        if not w in w_paid:
            not_paid_email.append(email[w])
            print("{0}: {1}".format(name[w], email[w]))


    print("{0} people have registered and {1} have paid.".format(len(w_isgoing),
                                                                 len(w_paid)))
    np.savetxt("./emails.csv", going_email, fmt="%s") 
    np.savetxt("./paid.csv", going_paid, fmt="%s") 
    np.savetxt("./not_paid_emails.csv", not_paid_email, fmt="%s") 
    np.savetxt("./names.csv", going_name, fmt="%s") 
    np.savetxt("./institutes.csv", going_institute, fmt="%s") 
    

def read_data(args):

    name = []
    institution = []
    gender = []
    event = []
    email = []
    paid = []
    payID = []

    isgoing = []

    print("")
    with open(args["fname_in"], 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            name.append(row[0])
            institution.append(row[1])
            gender.append(row[2])
            event.append(row[3])
            email.append(row[4])
            paid.append(row[6])
            payID.append(row[7])

            if "HWSA" in row[3]: 
                isgoing.append(True)
            else:
                isgoing.append(False)

    w = np.where(isgoing)[0]
   
    name = np.asarray(name)
    gender = np.asarray(gender)
    institution = np.asarray(institution)

    data = {}
    data["name"] = name[w]
    data["gender"] = gender[w]
    data["institution"] = institution[w]

    return data


if __name__ == '__main__':

    args = parse_inputs()

    data = read_data(args)

    check_payments(args)
