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
    """ Run the WW code for different cases.
    """
    log.basicConfig(level=log.WARNING) # Set logging level
    ROOT.EnableImplicitMT() # Enable multithreading in RDataFrame
    ROOT.gROOT.SetBatch(True) # Don't show graphics at runtime

    # Input
    tree_name = "WWObservables"
    energy = 250
    path_LR = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/4f_WW_sl/4f_WW_sl_eL_pR.root"
    path_RL = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/4f_WW_sl/4f_WW_sl_eR_pL.root"
    input_LR = IH.InputInfo(path_LR, tree_name, energy)
    input_RL = IH.InputInfo(path_RL, tree_name, energy)
    inputs = [input_LR, input_RL]

    # Triple Gauge Coupling configurations
    TGC_config_path = "/afs/desy.de/group/flc/pool/beyerjac/TGCAnalysis/SampleProduction/MCProduction/PrEWSampleProduction/scripts/config/tgc.config"
    TGC_points_path = "/afs/desy.de/group/flc/pool/beyerjac/TGCAnalysis/SampleProduction/MCProduction/PrEWSampleProduction/scripts/config/tgc_dev_points_g1z_ka_la.config"
    TGC_weight_base = "rescan_weights.weight"
    phys_options = PPO.PhysicsOptions(use_TGCs=True, TGC_config_path=TGC_config_path, TGC_points_path=TGC_points_path, TGC_weight_base=TGC_weight_base) )

    # Output settings
    output_dir = "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/NewMCProduction/4f_WW_sl/PrEWInput"
    create_plots = True

    # Coordinates
    coords = [
        DH.Coordinate("costh_Wminus_star", 20, -1.0, 1.0),
        DH.Coordinate("costh_l_star", 10, -1.0, 1.0),
        DH.Coordinate("phi_l_star", 10, -math.pi, math.pi),
    ]

    # Create all WW distributions
    for input in inputs:
      CPI.create_PrEW_input(
        input = input, coords = coords,
        output = OH.OutputInfo( output_dir, distr_name = "WW_muminus", create_plots = create_plots),
        cuts = "(decay_to_mu == 1) && (l_charge == -1)",
        syst = SSO.SystematicsOptions(use_muon_acc=True,costh_branch="costh_l"),
        phys = phys_options)
      CPI.create_PrEW_input(
        input = input, coords = coords,
        output = OH.OutputInfo( output_dir, distr_name = "WW_muplus", create_plots = create_plots),
        cuts = "(decay_to_mu == 1) && (l_charge == +1)",
        syst = SSO.SystematicsOptions(use_muon_acc=True,costh_branch="costh_l"),
        phys = phys_options)
      CPI.create_PrEW_input(
        input = input, coords = coords,
        output = OH.OutputInfo( output_dir, distr_name = "WW_tauminus", create_plots = create_plots),
        cuts = "(decay_to_tau == 1) && (l_charge == -1)",
        phys = phys_options)
      CPI.create_PrEW_input(
        input = input, coords = coords,
        output = OH.OutputInfo( output_dir, distr_name = "WW_tauplus", create_plots = create_plots),
        cuts = "(decay_to_tau == 1) && (l_charge == +1)",
        phys = phys_options)

    print("Done.")

# ------------------------------------------------------------------------------

# If this script is called directly (not imported), call the main funciton
if __name__ == "__main__":
    main()
