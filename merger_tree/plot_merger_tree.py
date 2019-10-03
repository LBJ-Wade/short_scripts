"""
This module plots a merger tree for an LHaloTree structured tree.

Dependencies
------------

matplotlib
numpy
networkx
pygraphviz (To get this, I had to `brew install graphviz` followed by
            `pip install pygraphviz`)

Author: Jacob Seiler
"""
#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import networkx as nx
import pygraphviz as pgv

import matplotlib as mpl
mpl.use('PS')  # This is necessary to get matplotlib working on Mac.
import matplotlib.cm as cm

class SimInfo(object):

    def __init__(self, name, max_num_parts=10000):
        """
        Parameters
        ----------

        name: string
            The name of the simulation.  Check the ``name.setter`` to see what simulations
            are implemented.

        max_num_parts: int
            For scaling the colourbar, the maximum halo mass is assumed to be the particle
            mass times ``max_num_parts``.  This assumption is checked when plotting the
            tree.
        """

        self._name = name

        if self.name == "Millennium":
            self.hubble_h = 0.73
            self.partmass = 0.0860657
            self.root_snapnum = 63
        elif self.name == "Kali":
            self.hubble_h = 0.6871
            self.partmass = 0.00078436
            self.root_snapnum = 98
        elif self.name == "Genesis":
            self.hubble_h = 0.6751
            self.partmass = 0.107
            self.root_snapnum = 131 

        # Convert particle mass to log10(Msun).
        self.partmass = np.log10(self.partmass * 1.0e10 / self.hubble_h)

        # The absolute minimum halo mass should use the particle mass.
        self.min_mass = self.partmass 

        # For the maximum halo mass, let's take N particles. May not be always
        # accurate, but should be a good indication. Can check this later.
        self.max_num_parts = max_num_parts
        self.max_mass = self.partmass + np.log10(max_num_parts)  # Careful of logs.

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        allowed_names = ["Kali", "Millennium"]

        if name not in allowed_names:
            print(f"The requested simulation name is {name}. The only allowed "
                  f"simulations are {allowed_name}")
            raise ValueError

        self._name = name


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


def read_tree(tree_path, tree_num=None, num_root_fofs=None, root_snap_num=None, 
              num_halos=0):
    """
    Reads specific LHaloTree tree.  Can be run in two modes:

    - A specific tree number (specified by ``tree_num``).
    - The first tree that has the specified number of FoF halos ``num_root_fofs`` at
      snapshot ``root_snap_num`` and a total number of halos greater or equal to
      ``num_halos``.

    Parameters
    ----------

    tree_path: string
        Path to the tree file.

    tree_num: int, optional
        If specified, will return a specific tree number.

    num_root_fofs, root_snap_num, num_halos: ints, optional
        If specified, will return the first tree that has at least ``num_root_fofs``
        halos at snapshot ``root_snap_num`` and a total number of halos greater or equal
        to ``num_halos``.

    Returns
    -------

    tree: LHalo structure, specified by :py:func:`~get_LHalo_datastruct`
        The specified tree.
    """

    # Default options will be tree 0.
    if tree_num is None and num_root_fofs is None:
        tree_num = 0

    # Can only EITHER ask for a specific tree or a tree with a certain number of root FoF
    # halos.
    if tree_num is not None and num_root_fofs:
        print(f"Only one of `tree_num` and `num_root_fofs` can be not `None. Current "
              f"values are {tree_num} and {num_root_fofs} respectively.")
        raise ValueError

    # Structure to hold the trees.
    LHalo_struct = get_LHalo_datastruct()

    with open(tree_path, "rb") as f_in:

        # First get header info.
        NTrees = np.fromfile(f_in, np.dtype(np.int32), 1)[0]
        NHalos = np.fromfile(f_in, np.dtype(np.int32), 1)[0]
        NHalosPerTree = np.fromfile(f_in, np.dtype((np.int32, NTrees)), 1)[0]

        # If we asked for a tree number that is greater than the number of trees, then we
        # can simply exit here.
        if tree_num is not None:
            if tree_num > NTrees:
                print(f"The number of trees in file {tree_path} is {NTrees}. You requested to "
                      f"return tree {tree_num}.")
                raise ValueError

        # Maybe the user asked for a tree with more halos than there are in ANY tree.
        if num_root_fofs is not None:
            if num_halos > np.max(NHalosPerTree):
                print(f"You requested a tree with at least {num_halos}. However, the "
                      f"maximum number of halos in any tree in file {tree_path} is "
                      f"{np.max(NHalosPerTree)}")
                raise ValueError

        # Search for the requested tree.
        for tree_idx in range(NTrees):

            tree = np.fromfile(f_in, LHalo_struct, NHalosPerTree[tree_idx])

            # If we're searching for a tree with a specified number of root FoFs, then
            # check number of FoFs.  Also check the total number of halos in the tree.
            if num_root_fofs is not None:
                if len(np.where(tree["SnapNum"][:] == root_snap_num)[0]) == num_root_fofs \
                    and len(tree) >= num_halos:
                    print(f"Tree {tree_idx} has {num_root_fofs} root FoFs and a total of "
                          f"{len(tree)} halos. Returning it.")
                    return tree

            # If we're searching for a specific tree and we're at that tree, return it.
            if tree_num is not None:
                if tree_idx == tree_num:
                    print(f"Returning tree {tree_num}")
                    return tree

    # If we reach here, we didn't hit the desired tree number or number of root FoFs somehow.
    print(f"After searching through all trees in {tree_path}, we could not find tree "
          f"number {tree_num} or a tree with {num_root_fofs} root FoFs and {num_halos} halos.")
    raise ValueError

    return None


def get_cmap_map(cmap_name, min_val, max_val, cmap_dir=None):
    """
    Gets a colormap and normalizes its values based on min/max values.

    E.g., ``m(0.5).to_rgba`` will return ``(R, G, B, A)`` values corresponding to the
    middle value of the colormap (after it has been normalized). 

    Parameters
    ----------

    cmap_name: string
        Name of the colormap being used.

    min_val, max_val: floats
        Minimum and maximum values used to normalize the colormap. These will be the
        bounds of the colormap.

    cmap_dir: string
        If specified, will attempt to import the colormaps inside this directory.
        Requires e13tools to be installed.

    Returns
    -------

    m: ``matplotlib.cm.ScalarMappable``
        A colormap map scaled by the min/max values.
    """

    # If the user has asked to import colormaps from a directory, check if e13tools is
    # installed.
    if cmap_dir is not None:
        try:
            from e13tools import import_cmaps
        except ImportError:        
            print("e13tools hasn't been installed and you specified a directory to import "
                  "cmaps from.. `pip install e13tools` if you want to import your own colormap.")
            raise ValueError
        else:
            # e13tools installed, let's import the colormaps.
            import_cmaps("./colormaps")

    cmap = cmap_name

    # Normalize the colormap between the specified values.
    norm = mpl.colors.Normalize(vmin=min_val, vmax=max_val)
    m = cm.ScalarMappable(norm=norm, cmap=cmap)

    return m


def convert_networkx_to_graphvis(networkx_graph, halos_per_snapshot):
    """
    Converts a ``networkx`` graph to a ``pygraphvis`` graph.  The nodes will be ranked
    based on the snapshot number.

    Parameters
    ----------

    networkx_graph: ``networkx.classes.graph.Graph``
        The ``networkx`` graph with nodes and edged populated.

    halos_per_snapshot: dict[int, list of ints]
        List of halos at each snapshot. Key is the snapshot number. 

    Returns
    -------

    A: ``pygraphviz.agraph.AGraph``
        ``pygraphviz`` graph with the nodes ranked by snapshot number.
    """

    # First convert the graph into a pygraphviz one.
    A = nx.nx_agraph.to_agraph(networkx_graph)

    # Now loop through each snapshot and add the ranks as subgraphs.
    for snapnum in halos_per_snapshot.keys():
        nodes_for_rank = halos_per_snapshot[snapnum]
        A.add_subgraph(nodes_for_rank, rank="same")

    return A


def plot_merger_tree(sim, tree, snapshots_to_plot, fname_out, cmap_map=None):
    """
    Plots a graph for a given LHaloTree ``tree`` at the specified snapshots.

    Parameters
    ----------

    sim: :py:class:`~SimInfo`
        Information about the simulation used for this tree.

    tree: LHalo structure, specified by :py:func:`~get_LHalo_datastruct`
        The tree being plotted.

    snapshots_to_plot: list or array-like of ints
        Only halos at these snapshots will be plotted.

    fname_out: string
        Name of the output file.

    cmap_map: ``matplotlib.cm.ScalarMappable``, optional
        If specified, uses the colormap to color the graph nodes based on halo mass.

    Generates
    ---------

    The graph saved as ``fname_out``.
    """

    # When we plot, we want to order them by their snapshots. When we go through the tree,
    # we will need to remember which halo is at which snapshot.
    halo_snapshot = {}

    # Our graph is drawing edges between each halo and its descendant. Hence let's just go
    # through each halo, and add an edge between the halo and the desc.
    G = nx.Graph()

    min_mass = 999
    max_mass = -999

    for halo_idx in range(len(tree)):

        snapnum = tree["SnapNum"][halo_idx]
        mass = tree["Mvir"][halo_idx] * 1.0e10 / sim.hubble_h

        # Don't care about this halo.
        if snapnum not in snapshots_to_plot:
            continue

        # Some halos haven't been assigned a mass despite having non-zero number of
        # particles (don't know why this is, email Volker Springel if you truly want to
        # know) . For these, use the number of particles * particle mass to determine
        # the mass.
        if mass < 1e-20:
            mass = tree["Len"][halo_idx] * sim.partmass * 1.0e10 / sim.hubble_h 

        # We've handled zero mass objects, so safe to log.
        mass = np.log10(mass)

        if mass > max_mass:
            max_mass = mass
        if mass < min_mass:
            min_mass = mass

        if cmap_map:
            # Map the mass to the RGB value of the defined colormap.
            # `rgba` returns (R, G, B, A) so take first 3 indices.
            rgb = cmap_map.to_rgba(mass)[:3]

            # Turn into hex '#XXXXXX' for pygraphvis.
            color = mpl.colors.rgb2hex(rgb)
        else:
            # Colour node whether the halo is the main FoF halo.
            if tree["FirstHaloInFOFgroup"][halo_idx] == halo_idx:
                color = "#FF0000"  # Red
            else:
                color = "#0000ff"  # Blue

        # The size of the graph nodes (the `width` property) is scaled by mass. To get
        # better distinction between masses, I put them into broad classes.
        if mass > 11:
            width = mass / 15
        elif mass > 11 and mass <= 12:
            width = mass / 20
        elif mass > 10 and mass <= 11:
            width = mass / 25
        elif mass > 9 and mass <= 10:
            width = mass / 30
        else:
            width = mass / 35

        # When we add the node, we don't want silly little labels. 
        G.add_node(halo_idx, snapnum=snapnum, color=color, width=width,
                   style="filled", shape="circle", fillcolor=color, label="")

        # Halos without descendants have `desc_idx == -1`.
        desc_idx = tree["Descendant"][halo_idx]
        if desc_idx != -1:
            G.add_edge(halo_idx, desc_idx)

        # Check to see if this snapshot has been added to the dictionary.
        try:
            halo_snapshot[snapnum].append(halo_idx)
        except KeyError:
            halo_snapshot[snapnum] = [halo_idx]

    """
    for halo_idx in range(len(tree)):

        snapnum = tree["SnapNum"][halo_idx]
        mass = np.log10(tree["Mvir"][halo_idx] * 1.0e10 / 0.6871)

        # Don't care about this halo.
        if snapnum not in snapshots_to_plot:
            continue

        # Also may want to add an edge to halos in the FoF group.
        nexthaloinfof_idx = tree["NextHaloInFOFgroup"][halo_idx]
        if nexthaloinfof_idx != -1:
            G.add_edge(halo_idx, nexthaloinfof_idx)
    """

    # When initializing the SimInfo class, we made an assumption about the maximum halo
    # mass. Check that this was correct. 
    if max_mass > sim.max_mass:
        print("")
        print(f"When initializing the SimInfo class, we assumed that the maximum halo "
              f"mass is {sim.max_num_parts} times the particle mass ({sim.max_num_parts} "
              f"* {sim.partmass} = {sim.max_mass:.3f} [log10Msun]).\nThe actual maximum mass was "
              f"{max_mass:.3f} [log10Msun]. To get nice scaling of colours, we recommend increasing the "
              f"value of `max_num_parts` in the `SimInfo` class `__init__` method.\nThe "
              f"maximum halo mass for this tree corresponds to "
              f"{pow(10, max_mass - sim.partmass):.0f} particles")
        print("")

    # The networkx graph has been constructed. We now want to turn it into a pygraphvis
    # graph and align all the halos by snapshot.
    graphvis_G = convert_networkx_to_graphvis(G, halo_snapshot)

    # Plot time!
    graphvis_G.draw(fname_out, prog="dot")
    print(f"Wrote plot to {fname_out}")


if __name__ == '__main__':

    # Get some information about the simulation we're using.
    sim = SimInfo("Millennium", max_num_parts=2e6)

    # When we plot the halo nodes, we want to color them based onstellar mass. Hence
    # let's first generate a map that will be used to do ``mass -> rgb value``. 
    cmap = "rainforest_r"  # Going to use Ellert's Rainforest colormap. Requires e13tools.
    cmap_dir = "./colormaps"  # Colormap is located in `./colormaps` directory.
    min_val = sim.min_mass  # log10(Msun).
    max_val = sim.max_mass  # log10(Msun).
    cmap_map = get_cmap_map(cmap, min_val, max_val, cmap_dir="./colormaps")

    # To make things easier and to make a better plot, let's read the first tree that has
    # exactly 1 FoF halo.
    #tree_path = "./subvolume_converted.43"
    tree_path = "./trees_063.0"
    tree_num = 0 
    num_root_fofs = None 
    root_snap_num = sim.root_snapnum
    num_halos = 0
    tree = read_tree(tree_path, tree_num=tree_num, num_root_fofs=num_root_fofs,
                     root_snap_num=root_snap_num, num_halos=num_halos)

    # Time to plot the tree.
    snapshots_to_plot = np.arange(0, root_snap_num+1)
    fname_out = "mill/complex_merger_tree.png"
    plot_merger_tree(sim, tree, snapshots_to_plot, fname_out, cmap_map=None) 
