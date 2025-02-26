#!/usr/bin/env python
"""
Code to create many trimmed model grids for batch runs
  Saves time by only reading the potentially huge modelsed grid once
  and only reads in the noisemodel/astfile if it has changed
"""

# system imports
import os
import argparse
import time

# BEAST imports
import beast.observationmodel.noisemodel.generic_noisemodel as noisemodel
from beast.fitting import trim_grid
from beast.physicsmodel.grid import FileSEDGrid


# datamodel only needed for the get_obscat function
# would be good to remove this dependence
import datamodel

if __name__ == "__main__":
    # commandline parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "trimfile", help="file with modelgrid, astfiles, obsfiles to use"
    )
    args = parser.parse_args()

    start_time = time.clock()

    # read in trim file
    f = open(args.trimfile, "r")
    file_lines = list(f)

    # physics model grid name
    modelfile = file_lines[0].rstrip()

    # get the modesedgrid on which to generate the noisemodel
    print("Reading the model grid files = ", modelfile)
    modelsedgrid = FileSEDGrid(modelfile)

    new_time = time.clock()
    print("time to read: ", (new_time - start_time) / 60.0, " min")

    old_noisefile = ""
    for k in range(1, len(file_lines)):

        print("/n/n")

        # file names
        noisefile, obsfile, astfile, filebase = file_lines[k].split()

        # make sure the proper directories exist
        if not os.path.isdir(os.path.dirname(filebase)):
            os.makedirs(os.path.dirname(filebase))

        # construct trimmed file names
        sed_trimname = filebase + "_sed_trim.grid.hd5"
        noisemodel_trimname = filebase + "_noisemodel_trim.hd5"

        print("working on " + sed_trimname)

        start_time = time.clock()

        if noisefile == old_noisefile:
            print("not reading noisefile - same as last")
            # print(noisefile)
            # print(astfile)
        else:
            print("reading noisefile/astfile")
            # read in the noise model
            noisemodel_vals = noisemodel.get_noisemodelcat(noisefile)
            old_noisefile = noisefile

        # read in the observed data
        print("getting the observed data")
        obsdata = datamodel.get_obscat(obsfile, modelsedgrid.filters)

        # trim the model sedgrid
        #   set n_detected = 0 to disable the trimming of models based on
        #      the ASTs (e.g. extrapolations are ok)
        #   this is needed as the ASTs in the NIR bands do not go faint enough
        trim_grid.trim_models(
            modelsedgrid,
            noisemodel_vals,
            obsdata,
            sed_trimname,
            noisemodel_trimname,
            sigma_fac=3.0,
        )

        new_time = time.clock()
        print("time to trim: ", (new_time - start_time) / 60.0, " min")
