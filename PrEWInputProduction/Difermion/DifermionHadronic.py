import ROOT
import logging as log
import math
import sys

# Local modules
sys.path.append("../Core")
import CreatePrEWInput as CPI
sys.path.append("../IO")
import InputHelpers as IH
import OutputHelpers as OH
sys.path.append("../ROOTHelp")
import DistrHelpers as DH

# ------------------------------------------------------------------------------

def main():
    """ Run the hadronic difermion code for different cases.
    """
    n_threads = 10 # Number of threads to use 
    
    log.basicConfig(level=log.WARNING) # Set logging level
    ROOT.EnableImplicitMT(n_threads) # Enable multithreading in RDataFrame
    ROOT.gROOT.SetBatch(True) # Don't show graphics at runtime

    # Input
    tree_name = "DifermionObservables"
    energy = 250
    path_LR = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/2f_Z_h/2f_Z_h_eL_pR.root"
    path_RL = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/2f_Z_h/2f_Z_h_eR_pL.root"
    input_LR = IH.InputInfo(path_LR, tree_name, energy)
    input_RL = IH.InputInfo(path_RL, tree_name, energy)
    inputs = [input_LR, input_RL]

    # Output settings
    output_dir = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/2f_Z_h/PrEWInput"
    create_plots = True

    # Coordinates
    coords = [
        DH.Coordinate("costh_f_star", 20, -1.0, 1.0)
    ]

    # Different final states and the cuts that identify them
    final_state_cuts = {
      "uds" : "((f_pdg == 1) || (f_pdg == 2) || (f_pdg == 3))",
      "c" : "(f_pdg == 4)",
      "b" : "(f_pdg == 5)"
    }
    
    # Mass ranges 
    mass_cuts = [
      [81, 101],
      [180, 1.1*energy]
    ]

    # Create distributions for opposite-sign chiralities (both charges)
    for input in inputs:
      for final_state, fs_cut in final_state_cuts.items():
        for m_low, m_high in mass_cuts:
          distr_name = "2f_{}_{}to{}".format(final_state,int(m_low),int(m_high))
          cuts = "{} && (m_ff > {}) && (m_ff < {})".format(fs_cut,m_low,m_high)
          CPI.create_PrEW_input(
            input = input, coords = coords, 
            output = OH.OutputInfo( output_dir, distr_name = distr_name, create_plots = create_plots), 
            cuts = cuts)

    print("Done.")

# ------------------------------------------------------------------------------

# If this script is called directly (not imported), call the main funciton
if __name__ == "__main__":
    main()
    