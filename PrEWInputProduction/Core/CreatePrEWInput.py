# ------------------------------------------------------------------------------

""" Script that holds the core function that creates the PrEW input CSV files.
"""

# ------------------------------------------------------------------------------

import logging as log
import ROOT
import pandas as pd
import sys

# Local modules
import Conventions as Conv
sys.path.append("../IO")
import CSVMetadata as CSVM
sys.path.append("../RKHelp")
import RKCoefMatcher as RKCM
sys.path.append("../ROOTHelp")
import DistrHelpers as DH
import DistrPlotting as DP
sys.path.append("../Systematics")
import MuonAcceptance as SMA
import SystematicsOptions as SSO

# ------------------------------------------------------------------------------

def create_PrEW_input(input, output, coords, cuts, 
                      syst=SSO.SystematicsOptions()):
  """ Create the input CSV distributions for PrEW by setting up an RDataFrame
      and extraction all relevant observables and coefficients and performing 
      the requested cuts.
  """
  
  # ----------------------- Create RDF and set commands ------------------------
  log.debug("Setting up RDataFrame instructions for {}".format(
      output.distr_name))
  
  # Read in the tree
  rdf = input.get_rdf()
  
  # Get simple metadata about the process
  n_total_ptr = rdf.Count()
  cross_section_ptr = rdf.Mean("cross_section")
  eM_chi_ptr = rdf.Mean("eM_chirality")
  eP_chi_ptr = rdf.Mean("eP_chirality")

  # Apply generator level cuts
  rdf_after_cuts = rdf.Filter(cuts)
  n_after_cuts_ptr = rdf_after_cuts.Count()

  # Create a RDataFrame histogram result pointer
  hist_ptr = DH.get_hist_ptr(rdf_after_cuts, output.distr_name, coords)

  # Prepare the muon acceptance box if requested
  muon_acc = None
  if syst.use_muon_acc:
    muon_acc_cut = SMA.default_acc_cut()
    muon_acc = SMA.MuonAccParametrisation(rdf_after_cuts, muon_acc_cut, 0.001, 
                                          syst.costh_branch, output.distr_name, coords)

  # ----------------------- Trigger RDF operations -----------------------------
  log.debug("Triggering RDataFrame operations.")
  
  # Get all the requested values
  n_total = n_total_ptr.GetValue()
  cross_section = cross_section_ptr.GetValue()
  eM_chi = eM_chi_ptr.GetValue()
  eP_chi = eP_chi_ptr.GetValue()
  n_after_cuts = n_after_cuts_ptr.GetValue()
  hist = hist_ptr.GetValue()

  print("For distr {}:\n\tBefore cuts: {} , after cuts: {} ({}%)".format(
      output.distr_name, n_total, n_after_cuts, n_after_cuts/n_total*100.0))

  # Base for output file name
  output_base_name = Conv.csv_file_name(output.distr_name, input.energy, 
                                      eM_chi, eP_chi)
  output_base = "{}/{}".format(output.dir, output_base_name)

  # Correctly normalize the histogram
  hist.Scale(cross_section/n_total)

  # Plot the histogram if requested
  if (output.create_plots):
    log.debug("Create histogram plot.")
    DP.draw_hist(hist, output, output_base_name)

  # ----------------------- Producing PrEW input -------------------------------
  log.debug("Start producing PrEW input.")

  # Extract bin centers and cross sections from the histogram
  data = DH.get_data(hist, coords)

  # Try to find coefficients from RK distribution
  coef_matcher = RKCM.default_coef_matcher()
  data = coef_matcher.add_coefs_to_data(output.distr_name, eM_chi, eP_chi, data)

  # Try extracting the differential coefficients for the muon acceptance box
  if muon_acc is not None:
    data = muon_acc.add_coefs_to_data(data)

  # Create a pandas dataframe
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

  if muon_acc is not None:
    muon_acc.add_coefs_to_metadata(metadata)

  metadata.write(file_path)
  log.debug("Done with distribution.")

# ------------------------------------------------------------------------------