import ROOT
import math
import numpy as np
import pandas as pd
import os
import sys

# Local modules
sys.path.append("../CommonHelpers")
import CSVMetadata as CSVM
import DistrHelpers as DH
import InputHelpers as IH
import OutputHelpers as OH

# ------------------------------------------------------------------------------

def create_WW_output(input, output, coords, cuts):
    # ----------------------- Create RDF and set commands ----------------------
    # Read in the tree
    rdf = input.get_rdf()
    n_total_ptr = rdf.Count()
    cross_section_ptr = rdf.Mean("cross_section")
    eM_chi_ptr = rdf.Mean("eM_chirality")
    eP_chi_ptr = rdf.Mean("eP_chirality")

    # Apply generator level cuts
    rdf_after_cuts = rdf.Filter(cuts)
    n_after_cuts_ptr = rdf_after_cuts.Count()

    # Create a RDataFrame histogram result pointer
    th3_ptr = DH.get_hist_ptr(rdf_after_cuts, output.distr_name, coords)

    # ----------------------- Trigger RDF operations ---------------------------
    # Get all the requested values
    n_total = n_total_ptr.GetValue()
    cross_section = cross_section_ptr.GetValue()
    eM_chi = eM_chi_ptr.GetValue()
    eP_chi = eP_chi_ptr.GetValue()
    n_after_cuts = n_after_cuts_ptr.GetValue()
    th3 = th3_ptr.GetValue()

    print("For distr {}:\n\tBefore cuts: {} , after cuts: {} ({}%)".format(
        output.distr_name, n_total, n_after_cuts, n_after_cuts/n_total*100.0))

    # Base for output file name
    output_base_name = DH.get_distr_filebase(output.distr_name, 
                                             input.energy, eM_chi, eP_chi)
    output_base = "{}/{}".format(output.dir, output_base_name)

    # Correctly normalize the TH3D
    th3.Scale(cross_section/n_total)

    if (output.create_plots):
        # Draw the TH3D
        canvas = ROOT.TCanvas("c_{}".format(output.distr_name))
        canvas.cd()
        th3.Draw("BOX2")

        # Save the TH3D
        plot_output_base = "{}/plots/{}".format(output.dir, output_base_name)
        canvas.Print("{}.pdf".format(plot_output_base))
        canvas.Print("{}.root".format(plot_output_base))

    # ----------------------- Producing PrEW input -----------------------------

    # Create a pandas dataframe
    data = DH.get_data(th3)
    df = pd.DataFrame(data)

    # Write the dataframe to a csv file
    file_path = "{}.csv".format(output_base)
    df.to_csv(file_path)

    # Attach metadata to beginning of file
    metadata = CSVM.CSVMetadata()
    metadata.add("name", output.distr_name)
    metadata.add("energy", input.energy)
    metadata.add("e- chirality", eM_chi)
    metadata.add("e+ chirality", eP_chi)
    metadata.write(file_path)

# ------------------------------------------------------------------------------

def main():
    """ Run the WW code for different cases.
    """
    ROOT.EnableImplicitMT() # Enable multithreading in RDataFrame

    # Input
    input = IH.InputInfo(
        file_path = "/home/jakob/Documents/DESY/MountPoints/DUSTMount/TGCAnalysis/SampleProduction/NewMCProduction/Test/WWtest.root",
        tree_name = "WWObservables", energy = 250)

    # Output settings
    output_dir = "/home/jakob/Documents/DESY/MountPoints/DUSTMount/TGCAnalysis/SampleProduction/NewMCProduction/WW"

    # Coordinates
    coords = [
        DH.Coordinate("costh_Wminus_star", 20, -1, 1),
        DH.Coordinate("costh_l_star", 20, -1, 1),
        DH.Coordinate("phi_l_star", 20, -math.pi, math.pi),
    ]

    # Create all WW distributions
    create_WW_output(
      input = input, coords = coords, 
      output = OH.OutputInfo( output_dir, distr_name = "WW_muminus"), 
      cuts = "(decay_to_mu == 1) && (l_charge == -1)")
    create_WW_output(
      input = input, coords = coords, 
      output = OH.OutputInfo( output_dir, distr_name = "WW_muplus"), 
      cuts = "(decay_to_mu == 1) && (l_charge == +1)")
    create_WW_output(
      input = input, coords = coords, 
      output = OH.OutputInfo( output_dir, distr_name = "WW_tauminus"), 
      cuts = "(decay_to_tau == 1) && (l_charge == -1)")
    create_WW_output(
      input = input, coords = coords, 
      output = OH.OutputInfo( output_dir, distr_name = "WW_tauplus"), 
      cuts = "(decay_to_tau == 1) && (l_charge == +1)")

    print("Done.")

# ------------------------------------------------------------------------------

# If this script is called directly (not imported), call the main funciton
if __name__ == "__main__":
    main()
    