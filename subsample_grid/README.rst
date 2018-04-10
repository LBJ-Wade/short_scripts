This script takes a binary grid and regrids it onto a coarser grid. 

To explain my definition of `subsample`, say we have a 1024^3 grid and want to
move to a 256^3 grid.  We will then split the 1024^3 grid into discrete
(non-overlapping) 8x8x8 cube.  The mean of each of these cubes will correspond
to the values of the new 256^3 grid. 

Please pay attention to the required format of the inputs. In particular, if 
there has not been an input or output grid specified a ValueError will be 
raised.

The only accepted arguments for `precision` is ``float`` or ``double``; any
other input (including no input at all) will raise a ValueError. Specifying
these inputs should be done without any apostrophes.  

If the size of the input grid is less than the size of the output grid a
ValueError will be raised. This is a subsampler.

If the size of the output grid is not a multiple of the input grid a
ValueError will be raised.

usage: subsample.py [-h] [-f FNAME_IN] [-o FNAME_OUT] [-p PRECISION]
                    [-s GRIDSIZE_IN] [-d GRIDSIZE_OUT]

optional arguments:
  -h, --help            show this help message and exit
  -f FNAME_IN, --fname_in FNAME_IN
                        Path to the input grid file. Required.
  -o FNAME_OUT, --fname_out FNAME_OUT
                        Path to the output grid file. Required.
  -p PRECISION, --precision PRECISION
                        Precision for the grids. Accepted values are 'float'
                        and 'double'. Required.
  -s GRIDSIZE_IN, --gridsize_in GRIDSIZE_IN
                        Size of the grid (i.e., number of cells per dimension)
                        of input grid. Required.
  -d GRIDSIZE_OUT, --gridsize_out GRIDSIZE_OUT
                        Size of the grid (i.e., number of cells per dimension)
                        of output grid. Required.

Example:
>>> python python3 subsample.py -f /lustre/projects/p004_swin/jseiler/kali/densfield_grids/1024/snap_48.dens.dat
    -o /lustre/projects/p134_swin/jseiler/kali/density_fields/1024_subsampled_256/snap048.dens.dat
    -p double --gridsize_in=1024 --gridsize_out=256 

