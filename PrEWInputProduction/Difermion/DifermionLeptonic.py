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

    # Mass cut ranges and FB cut for return-to-Z
    mass_cuts = {
      "return-to-Z" : [81, 101],
      "high-Q2" : [180, 1.1*energy]
    }
    
    # for m_low, m_high in mass_cuts:
    cut_dict = {}
    for mass_range_name, cut_value in mass_cuts.items():
      m_low, m_high = cut_value
      mass_cut_name = "{}to{}".format(int(m_low),int(m_high))
      mass_cut = "(m_ff > {}) && (m_ff < {})".format(m_low, m_high)
      
      if mass_range_name == "return-to-Z":
        # For return-to-Z with string ISR, split forward and backward Pz_ff
        forward_cut_name = "{}_FZ".format(mass_cut_name)
        backward_cut_name = "{}_BZ".format(mass_cut_name)
        forward_cut = "{} && (pz_ff > 0)".format(mass_cut)
        backward_cut = "{} && (pz_ff < 0)".format(mass_cut)
        cut_dict[forward_cut_name] = forward_cut
        cut_dict[backward_cut_name] = backward_cut
      else:
        # For high-Q^2 no further splitting
        cut_dict[mass_cut_name] = mass_cut
      
    
    # --- Muons (w/ systematics) ------------------------------------------------
    for input in inputs:
      for cut_name, cuts in cut_dict.items():
        distr_name = "2f_mu_{}".format(cut_name)
        distr_cuts = "(f_pdg == 13) && {}".format(cuts)
        CPI.create_PrEW_input(
          input = input, coords = coords, 
          output = OH.OutputInfo( output_dir, distr_name = distr_name, create_plots = create_plots), 
          cuts = distr_cuts, 
          syst = SSO.SystematicsOptions(use_muon_acc=True,costh_branch=["costh_f","costh_fbar"]))
      
    # --- Taus (no systematics) ------------------------------------------------
    for input in inputs:
      for cut_name, cuts in cut_dict.items():
        distr_name = "2f_tau_{}".format(cut_name)
        distr_cuts = "(f_pdg == 15) && {}".format(cuts)
        CPI.create_PrEW_input(
          input = input, coords = coords, 
          output = OH.OutputInfo( output_dir, distr_name = distr_name, create_plots = create_plots), 
          cuts = distr_cuts)
    
    print("Done.")

# ------------------------------------------------------------------------------

# If this script is called directly (not imported), call the main funciton
if __name__ == "__main__":
    main()
    