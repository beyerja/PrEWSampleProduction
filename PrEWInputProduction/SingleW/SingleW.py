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
    """ Run the SingleW code for different cases.
    """
    log.basicConfig(level=log.WARNING) # Set logging level
    ROOT.EnableImplicitMT() # Enable multithreading in RDataFrame
    ROOT.gROOT.SetBatch(True) # Don't show graphics at runtime

    # Input
    tree_name = "SingleWObservables"
    energy = 250
    path_LR = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/4f_sW_sl/4f_sW_sl_eL_pR.root"
    path_RL = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/4f_sW_sl/4f_sW_sl_eR_pL.root"
    path_LL = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/4f_sW_sl/4f_sW_sl_eL_pL.root"
    path_RR = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/4f_sW_sl/4f_sW_sl_eR_pR.root"
    input_LR = IH.InputInfo(path_LR, tree_name, energy)
    input_RL = IH.InputInfo(path_RL, tree_name, energy)
    input_LL = IH.InputInfo(path_RL, tree_name, energy)
    input_RR = IH.InputInfo(path_RL, tree_name, energy)
    inputs_os = [input_LR, input_RL] # Opposite sign chirality infos

    # Output settings
    output_dir = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/4f_sW_sl/PrEWInput"
    create_plots = True

    # Coordinates
    coords = [
        DH.Coordinate("costh_Whad_star", -0.9695290858725761, 0.9695290858725761),
        DH.Coordinate("costh_e_star", 10, -0.925925925925926, 0.925925925925926),
        DH.Coordinate("m_enu", 20, 4.037857055, 165.55213928499998),
    ]

    # Create distributions for opposite-sign chiralities (both charges)
    for input in inputs_os:
      CPI.create_PrEW_input(
        input = input, coords = coords, 
        output = OH.OutputInfo( output_dir, distr_name = "SingleW_eminus", create_plots = create_plots), 
        cuts = "(e_charge == -1)")
      CPI.create_PrEW_input(
        input = input, coords = coords, 
        output = OH.OutputInfo( output_dir, distr_name = "SingleW_eplus", create_plots = create_plots), 
        cuts = "(e_charge == +1)")

    # Create distributions for same-sign chiralities
    CPI.create_PrEW_input(
      input = input_RR, coords = coords, 
      output = OH.OutputInfo( output_dir, distr_name = "SingleW_eminus", create_plots = create_plots), 
      cuts = "(e_charge == -1)")
    CPI.create_PrEW_input(
      input = input_LL, coords = coords, 
      output = OH.OutputInfo( output_dir, distr_name = "SingleW_eplus", create_plots = create_plots), 
      cuts = "(e_charge == +1)")
    
    print("Done.")

# ------------------------------------------------------------------------------

# If this script is called directly (not imported), call the main funciton
if __name__ == "__main__":
    main()
    