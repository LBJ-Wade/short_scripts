#!/usr/bin/env python
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import numpy as np


def read_binary_grid(filepath, GridSize, precision, reshape=True):
    '''
    Reads a cubic, Cartesian grid that was stored in binary.
    NOTE: Assumes the grid has equal number of cells in each dimension.

    Parameters
    ----------
    filepath : string
        Location of the grid file
    GridSize : integer
        Number of cells along one dimension.  Grid is assumed to be saved in the form N*N*N.
    precision : integer
        Denotes the precision of the data being read in.
        0 : Integer (4 bytes)
        1 : Float (4 bytes)
        2 : Double (8 bytes)
    reshape : boolean
        Controls whether the array should be reshaped into a cubic array of shape (GridSize, GridSize, GridSize) or kepts as a 1D array.
        Default: True.

    Returns
    -------
    grid : `np.darray'
	The read in grid as a numpy object.  Shape will be N*N*N.
    '''

    ## Set the format the input file is in. ##
    readformat = 'None'
    if precision == 0:
        readformat = np.int32
        byte_size = 4
    elif precision == 1:
        readformat = np.float32
        byte_size = 4
    elif precision == 2:
        readformat = np.float64
        byte_size = 8
    else:
        print("You specified a read format of %d" %(precision))
        raise ValueError("Only 0, 1, 2 (corresponding to integers, float or doubles respectively) are currently supported.")

    ## Check that the file is the correct size. ##
    filesize = os.stat(filepath).st_size
    expected_size = GridSize*GridSize*GridSize*byte_size

    if(expected_size != filesize):
        print("The size of file {0} is {1} bytes whereas we expected it to be "
              "{2} bytes".format(filepath, filesize, expected_size))
        raise ValueError("Mismatch between size of file and expected size.")

    fd = open(filepath, 'rb')
    grid = np.fromfile(fd, count = GridSize**3, dtype = readformat)
    if (reshape == True):
        grid = np.reshape(grid, (GridSize, GridSize, GridSize), order="F")
    fd.close()

    return grid



def plot_density_slice(density_path, snapshot, gridsize, slice_idx, slice_thickness,
                       boxsize, double_precision, output_fname):

    #density_fname = f"{density_path}{snapshot:03}.dens.dat"
    density_fname = f"{density_path}_{snapshot}.dens.dat"

    if double_precision:
        precision = 2
    else:
        precision = 1

    print("Reading grid.")
    density = read_binary_grid(density_fname, gridsize, precision)

    print("Making plot.")
    # Time to plot.

    fig1 = plt.figure()
    ax = fig1.add_subplot(111)

    my_slice = np.log10(density[:,:,slice_idx:slice_idx+slice_thickness].mean(axis=-1))

    min_dens = np.min(my_slice)
    max_dens = np.max(my_slice)

    print(min_dens)

    min_dens = -1.2
    if max_dens > 1.5:
        max_dens = 1.5

    labelsize = 20

    im = ax.imshow(my_slice,
                   interpolation="none", origin="low",
                   extent = [0.0, boxsize, 0.0, boxsize],
                   vmin=min_dens, vmax=max_dens, cmap="Purples")

    ax.set_xlim([0.0, boxsize])
    ax.set_ylim([0.0, boxsize])

    #plt.axis("off")
    ax.set_xlabel(r"$\mathbf{x \: [h^{-1}Mpc]}$", size=labelsize)
    ax.set_ylabel(r"$\mathbf{y \: [h^{-1}Mpc]}$", size=labelsize)

    # Now lets fix up the colorbar.
    #cax = fig1.add_axes([0.81, 0.11, 0.03, 0.77])
    #ticks = [-4, -3, -2, -1, 0, 1]
    ticks = np.arange(np.floor(min_dens), np.ceil(max_dens+1.0), 1.0)
    cbar = fig1.colorbar(im, ticks=ticks)
    cbar.ax.set_yticklabels([r"$\mathbf{%d}$" % x for x in ticks],
                            fontsize = 10)
    cbar.ax.set_ylabel(r'$\mathbf{\log_{10} \left(\rho/\langle \rho\rangle\right)}$',
                       rotation = 90, size = 10)
    cbar.ax.tick_params(labelsize = 10)

    tick_locs = np.arange(0, 110, 20)
    ax.set_yticklabels([r"$\mathbf{%d}$" % x for x in tick_locs],
                       fontsize = 10)
    ax.set_xticklabels([r"$\mathbf{%d}$" % x for x in tick_locs],
                       fontsize = 10)


    # Finally add the redshift to the top right of the axis.
    z_label = r"$z = 5.83$"
    #z_text = ax.text(0.80,0.9, z_label,
    #                 transform=ax.transAxes,
    #                 size=12,
    #                 color='k')
    # Add a white background to make the label legible.
    #z_text.set_path_effects([PathEffects.withStroke(linewidth=5, foreground='w')])
    plt.draw()

    plt.tight_layout()

    fig1.savefig(output_fname)
    print(f"Saved {output_fname}")

if __name__ == "__main__":

    #density_path = "/fred/oz004/jseiler/kali/density_fields/1024_subsampled_256/snap"
    density_path = "/fred/oz004/jseiler/kali/density_fields/1024/snap"
    snapshot = 98
    gridsize = 1024
    double = True

    output_fname = f"./plots/density_{snapshot:03}.png"

    plot_density_slice(density_path, snapshot, gridsize, 128, 1, 108.08, double, output_fname)
