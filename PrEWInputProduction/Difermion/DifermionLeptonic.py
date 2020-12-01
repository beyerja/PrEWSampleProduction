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
sys.path.append("../Systematics")
import SystematicsOptions as SSO

# ------------------------------------------------------------------------------

def main():
    """ Run the leptonic difermion code for different cases.
    """
    n_threads = 10 # Number of threads to use 
    
    log.basicConfig(level=log.WARNING) # Set logging level
    ROOT.EnableImplicitMT(n_threads) # Enable multithreading in RDataFrame
    ROOT.gROOT.SetBatch(True) # Don't show graphics at runtime

    # Input
    tree_name = "DifermionObservables"
    energy = 250
    path_LR = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/2f_Z_l/2f_Z_l_eL_pR.root"
    path_RL = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/2f_Z_l/2f_Z_l_eR_pL.root"
    input_LR = IH.InputInfo(path_LR, tree_name, energy)
    input_RL = IH.InputInfo(path_RL, tree_name, energy)
    inputs = [input_LR, input_RL]

    # Output settings
    output_dir = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/2f_Z_l/PrEWInput"
    create_plots = True

    # Coordinates
    coords = [
        DH.Coordinate("costh_f_star", 20, -1.0, 1.0)
    ]

    # Mass ranges 
    mass_cuts = [
      [81, 101],
      [180, 1.1*energy]
    ]
    
    # --- Muons (w/ systematics) ------------------------------------------------
    for input in inputs:
      for m_low, m_high in mass_cuts:
        distr_name = "2f_mu_{}to{}".format(final_state,int(m_low),int(m_high))
        cuts = "(f_pdg == 13) && (m_ff > {}) && (m_ff < {})".format(fs_cut,m_low,m_high)
        CPI.create_PrEW_input(
          input = input, coords = coords, 
          output = OH.OutputInfo( output_dir, distr_name = distr_name, create_plots = create_plots), 
          cuts = cuts, 
          syst = SSO.SystematicsOptions(use_muon_acc=True,costh_branch=["costh_f","costh_fbar"]))
        
    # --- Taus (no systematics) ------------------------------------------------
    for input in inputs:
      for m_low, m_high in mass_cuts:
        distr_name = "2f_tau_{}to{}".format(final_state,int(m_low),int(m_high))
        cuts = "(f_pdg == 15) && (m_ff > {}) && (m_ff < {})".format(fs_cut,m_low,m_high)
        CPI.create_PrEW_input(
          input = input, coords = coords, 
          output = OH.OutputInfo( output_dir, distr_name = distr_name, create_plots = create_plots), 
          cuts = cuts)
    
    print("Done.")

# ------------------------------------------------------------------------------

# If this script is called directly (not imported), call the main funciton
if __name__ == "__main__":
    main()
    