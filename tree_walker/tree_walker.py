#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import networkx as nx
from matplotlib import pyplot as plt


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

def read_tree(tree_path, tree_num=None, num_root_fofs=None, root_snap_num=None):

    if tree_num and num_root_fofs:
        print(f"Only one of `tree_num` and `num_root_fofs` can be not `None. Current "
              f"values are {tree_num} and {num_root_fofs} respectively.")
        raise ValueError

    if num_root_fofs and not root_snap_num:
        print(f"If selecting a tree based on the number of root FoFs, `root_snap_num` "
              f"must be specified.")
        raise ValueError

    LHalo_struct = get_LHalo_datastruct()

    with open(tree_path, "rb") as f_in:

        # First get header info.
        NTrees = np.fromfile(f_in, np.dtype(np.int32), 1)[0]
        NHalos = np.fromfile(f_in, np.dtype(np.int32), 1)[0]
        NHalosPerTree = np.fromfile(f_in, np.dtype((np.int32, NTrees)), 1)[0]

        max_halos_tree = np.argmax(NHalosPerTree)
        print(f"Max halos is {NHalosPerTree[max_halos_tree]} for tree {max_halos_tree}")
        return

        if tree_num:
            if tree_num > NTrees:
                print(f"The number of trees in file {tree_path} is {NTrees}. You requested to "
                      f"return tree {tree_num}.")
                raise ValueError

        # We could be sneaky and `fseek` to the correct point in the file. However, because
        # I'm lazy, I'm just going to iterate over the trees until we reach the desired one.
        for tree_idx in range(NTrees):

            tree = np.fromfile(f_in, LHalo_struct, NHalosPerTree[tree_idx])

            if num_root_fofs is not None:
                if len(np.where(tree["SnapNum"][:] == root_snap_num)[0]) == num_root_fofs \
                    and len(tree) > 1000:
                    print(f"Tree {tree_idx} has {num_root_fofs} root FoFs and a total of "
                          f"{len(tree)} halos. Returning it.")
                    print(f"{tree_path}")
                    #return tree

            if tree_num:
                if tree_idx == tree_num:
                    print(f"Returning tree {tree_num}")
                    return tree

    # If we reach here, we didn't hit the desired tree number or number of root FoFs somehow.
    #print(f"After searching through all trees in {tree_path}, we could not find tree "
    #      f"number {tree_num} or a tree with {num_root_fofs} root FoFs.")
    #raise ValueError

    return None


def fully_walk_tree(start_idx, tree):
    """
    Code taken from https://github.com/manodeep/LHaloTreeReader
    """

    curr_halo = start_idx

    if tree["FirstProgenitor"][curr_halo] != -1:
        return tree[curr_halo]["FirstProgenitor"]

    if tree["NextProgenitor"][curr_halo] != -1:
        return tree["NextProgenitor"][curr_halo]

    while tree["NextProgenitor"][curr_halo] == -1 and tree["Descendant"][curr_halo] != -1:
        curr_halo = tree["Descendant"][curr_halo]

    return tree["NextProgenitor"][curr_halo]


def plot_graph(G, plot_output_path, plot_output_format="png"):

    fig = plt.figure(figsize=(16,16))
    ax = fig.add_subplot(111)

    """
    pos = nx.spring_layout(G)

    for node_num in pos.keys():
        pos[node_num][1] = G.nodes[node_num]["snapnum"]
    """
    nx.draw_networkx(G, pos)

    fig.tight_layout()

    output_file = "{0}/merger_tree.{1}".format(plot_output_path, plot_output_format)
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()


if __name__ == '__main__':

    # To make things easier and to make a better plot, let's read the first tree that has
    # exactly 1 FoF halo.
    trees = np.arange(0, 64)
    tree_path = "/fred/oz004/jseiler/kali/shifted_trees/subgroup_trees_000.dat"
    num_root_fofs = 1
    root_snap_num = 98
    #tree = read_tree(tree_path, num_root_fofs=num_root_fofs, root_snap_num=root_snap_num)
    for suffix in trees:
        print(f"{suffix}")
        path = f"/fred/oz004/jseiler/kali/shifted_trees/subgroup_trees_{suffix:03}.dat"
        read_tree(path, num_root_fofs=num_root_fofs, root_snap_num=root_snap_num)
    exit()
    # Initialize the graph.
    G = nx.Graph()

    # When we plot, we want to order them by their snapshots. When we go through the tree,
    # we will need to remember which halo is at which snapshot.
    halo_snapshot = {}

    # Our graph is drawing edges between each halo and its descendant. Hence let's just go
    # through each halo, and add an edge between the halo and the desc.
    for halo_idx in range(len(tree)):

        snapnum = tree["SnapNum"][halo_idx]
        G.add_node(halo_idx, snapnum=snapnum)

        desc_idx = tree["Descendant"][halo_idx]
        # Halos without descendants have `desc_idx == -1`.
        if desc_idx != -1:
            G.add_edge(halo_idx, desc_idx, )

        # Check to see if this snapshot has been added to the dictionary.
        try:
            halo_snapshot[snapnum].append(halo_idx)
        except KeyError:
            halo_snapshot[snapnum] = [halo_idx]

    # We will now add the ranks to ensure the graph is ordered by snapshot.

    # First convert the graph into a pygraphviz one.
    A = nx.to_agraph(G)

    # Now loop through each snapshot and add the ranks as subgraphs.
    for snapnum in halo_snapshot.keys():
        nodes_for_rank = halo_snapshot[snapnum]
        _ = A.add_subgraph(nodes_for_rank, rank="same")

    A.draw("plots/merger_tree.png")
    print("EOHROQEJ")
