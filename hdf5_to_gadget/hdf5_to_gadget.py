#!/usr/bin:env python
from __future__ import print_function
import numpy as np
import h5py
from tqdm import tqdm
import argparse
import time
from array import array
import numpy as np

def get_fname(snap, chunk, outdir):

    if snap < 66: # Slightly different naming scheme depending upon the snapshot.
        fname= "{0}/snapdir_{1:03d}/snapdir_{1:03d}/snapshot_{1:03d}.{2}.hdf5".format(snapdir,
                                                                                      snap,
                                                                                      chunk)
    else:
        fname = "{0}/snapdir_{1:03d}/snapshot_{1:03d}.{2}.hdf5".format(snapdir,
                                                                       snap,
                                                                       chunk)


    fname_in = fname 
    fname_out = "{0}/snapdir_{1:03d}/snapshot_{1:03d}.{2}.hdf5".format(outdir, snap, chunk)

    return fname_in, fname_out 


def write_header(fname_in, fname_out):

    with h5py.File(fname_in, "r") as f_in:
        npart_total = f_in["Header"].attrs["NumPart_Total"]
        npart_total_highword = f_in["Header"].attrs["NumPart_Total_HighWord"]
        npart_thisfile = f_in["Header"].attrs["NumPart_ThisFile"]
        masstable = f_in["Header"].attrs["MassTable"]

        for i in range(6):
            if i == 1:
                continue
            npart_total[i] = 0
            npart_total_highword[i] = 0
            npart_thisfile[i] = 0
            masstable[i] = 0
       
        fout = open(fname_out, "wb")

        x = np.array(256).astype(np.int32)
        x.tofile(fout)

        npart = np.array(npart_thisfile).astype(np.int32)
        npart.tofile(fout) 
    
        mass = np.array(masstable).astype(np.float64)
        mass.tofile(fout)

        time = np.array(f_in["Header"].attrs["Time"]).astype(np.float64)
        time.tofile(fout)

        redshift = np.array(f_in["Header"].attrs["Redshift"]).astype(np.float64)
        redshift.tofile(fout)

        Flag_Sfr = np.array(f_in["Header"].attrs["Flag_Sfr"]).astype(np.int32)
        Flag_Sfr.tofile(fout)

        Flag_Feedback = np.array(f_in["Header"].attrs["Flag_Feedback"]).astype(np.int32)
        Flag_Feedback.tofile(fout)

        npart_tot = np.array(npart_total).astype(np.int32)
        npart_tot.tofile(fout) 
         
        Flag_Cooling= np.array(f_in["Header"].attrs["Flag_Cooling"]).astype(np.int32)
        Flag_Cooling.tofile(fout)

        NumFiles = np.array(f_in["Header"].attrs["NumFilesPerSnapshot"]).astype(np.int32)
        NumFiles.tofile(fout)

        boxsize = np.array(f_in["Header"].attrs["BoxSize"]).astype(np.float64)
        boxsize.tofile(fout)

        Omega0 = np.array(f_in["Header"].attrs["Omega0"]).astype(np.float64)
        Omega0.tofile(fout)

        OmegaLambda= np.array(f_in["Header"].attrs["OmegaLambda"]).astype(np.float64)
        OmegaLambda.tofile(fout)
       
        HubbleParam = np.array(f_in["Header"].attrs["HubbleParam"]).astype(np.float64)
        HubbleParam.tofile(fout)
        
        StellarAge = np.array(f_in["Header"].attrs["Flag_StellarAge"]).astype(np.int32)
        StellarAge.tofile(fout)
        
        metals = np.array(f_in["Header"].attrs["Flag_Metals"]).astype(np.int32)
        metals.tofile(fout)

        npart_tot_hw = np.array(npart_total_highword).astype(np.int32)
        npart_tot_hw.tofile(fout) 
    
        entropy = np.array(0).astype(np.int32)
        entropy.tofile(fout)
               
        fill = np.array(np.zeros(int(60/4))).astype(np.int32)  # Pad to 256.
        fill.tofile(fout)

        x.tofile(fout) 
 
        fout.close()


def write_field(fname_in, fname_out, field): 

    with h5py.File(fname_in, "r") as f_in:
        fout = open(fname_out, "ab")

        npart_thisfile = f_in["Header"].attrs["NumPart_ThisFile"][1]
        field_data = f_in["PartType1"][field][:]

        # Write 3 floats per particle for Pos.
        # -> NumberBytes = npart * 4 * 3.

        # Write 1 longIDs per particle for IDs. 
        # -> NumberBytes = npart * 8.

        if "ID" in field.upper():
            nbytes = np.array(npart_thisfile * 8).astype(np.int32)
            data = np.array(field_data).astype(np.int64)
        else:
            nbytes = np.array(npart_thisfile * 4 * 3).astype(np.int32)
            data = np.array(field_data).astype(np.float32)

        nbytes.tofile(fout)
        data.tofile(fout) 
        nbytes.tofile(fout)

 
def write_binary(SnapLow, SnapHigh, num_chunks, snapdir, outdir, fields):

    for snap in range(SnapLow, SnapHigh + 1):
        for chunk in tqdm(range(num_chunks)):
            fname_in, fname_out = get_fname(snap, chunk, outdir)
            write_header(fname_in, fname_out)
            
            for field in fields: 
                write_field(fname_in, fname_out, field) 

if __name__ == '__main__':

    SnapLow=40
    SnapHigh=40
    num_chunks=1
    snapdir="/lustre/projects/p134_swin/jseiler/simulations/1.6Gpc/means/halo_1721673/dm_gadget/data"
    outdir="/lustre/projects/p004_swin/jseiler/britton_binary"
    fields=["Coordinates", "ParticleIDs"]

    write_binary(SnapLow, SnapHigh, num_chunks, snapdir, outdir, fields)
 
