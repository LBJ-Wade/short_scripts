This script takes the z = 0 matter power spectrum output of ``CAMB`` and
evolves it to a specified redshift z.  

usage: calc_pspec.py [-h] [-f CAMB_IN] [-z REDSHIFT] [-o FNAME_OUT]

optional arguments:
  -h, --help            show this help message and exit
  -f CAMB_IN, --camb_in CAMB_IN
                        Path to the input matter power spectrum from CAMB.
                        Required.
  -z REDSHIFT, --redshift REDSHIFT
                        Redshift we're calculating the power spectrum for.
                        Required.
  -o FNAME_OUT, --fname_out FNAME_OUT
                        Path to the ouput file. Required.

Example:

.. code-block:: python
>>> python calc_pspec.py -f /Users/100921091/Desktop/CAMB-0.1.6.1/kali_matterpower.dat 
    -z 9.918 -o ./snap048_matterpower
