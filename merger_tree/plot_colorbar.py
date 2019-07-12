#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import matplotlib as mpl
mpl.use('PS')
import matplotlib.cm as cm
import matplotlib.pyplot as plt

from plot_merger_tree import get_cmap_map


def plot_vert_colorbar(cmap, min_val, max_val, fname_out):
    """
    Plots just a vertical colorbar.

    Parameters
    ----------

    cmap: string
        Name of the colormap being used.

    min_val, max_val: ints
        Minimum and maximum values of the colorbar.

    fname_out: string
        Name of the output file.

    Generates
    ---------

    Saves a plot of the colorbar named ``fname_out``.
    """

    fig = plt.figure(figsize=(8, 12))
    ax1 = fig.add_axes([0.4, 0.05, 0.15, 0.9])

    norm = mpl.colors.Normalize(vmin=min_val, vmax=max_val)

    cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm,
                                    orientation='vertical')
    cb1.set_label(r'$\mathbf{\log_{10} Halo \: Mass \: [\mathrm{M}_\odot]}$', fontsize=30)
    ticks = np.arange(min_val, max_val+1, 1)
    cb1.ax.set_yticklabels([r"$\mathbf{%d}$" % x for x in ticks], fontsize=30)

    fig.savefig(fname_out)
    print(f"Saved file to {fname_out}")
    plt.close()


if __name__ == '__main__':

    # Get the colormap and its normalization values. 
    cmap = "rainforest_r"  # Going to use Ellert's Rainforest colormap. Requires e13tools.
    cmap_dir = "./colormaps"  # Colormap is located in `./colormaps` directory.
    min_val = 7  # log10(Msun).
    max_val = 12  # log10(Msun).
    cmap_map = get_cmap_map(cmap, min_val, max_val, cmap_dir="./colormaps")

    # Now plot the colorbar.
    fname_out = "plots/colorbar.png"
    plot_vert_colorbar(cmap, min_val, max_val, fname_out)
