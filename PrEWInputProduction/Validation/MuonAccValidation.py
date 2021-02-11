# ------------------------------------------------------------------------------

""" Code to validate the Muon acceptance parametrisation.
"""

# ------------------------------------------------------------------------------

import ctypes
import logging as log
import numpy as np
import pandas as pd
import sys

# Local modules
sys.path.append("../IO")
import CSVMetadata as CSVM
import OutputHelpers as OH
sys.path.append("../ROOTHelp")
import DistrHelpers as DH
sys.path.append("../Systematics")
import MuonAcceptance as SMA

# ------------------------------------------------------------------------------

def muon_acc_factor(k_0, k_c, k_w, k_c2, k_w2, k_cw, delta_c, delta_w):
  """ Return the factor by which a bin needs to be multiplied, given all the 
      needed coefficients and the deviations in center and width.
  """
  return k_0 + k_c * delta_c + k_w * delta_w \
         + k_c2 * delta_c**2 + k_w2 * delta_w**2 \
         + k_cw * delta_c * delta_w 
  
def binned_muon_acc_factors(coef_data, delta_c, delta_w):
  """ Get the binned factors (to multiple histogram bins with) for the given 
      coefficients and given changes in central and width values.
  """
  
  # Extract binned coefficients
  k_0 = np.array(coef_data["Coef:MuonAcc_k0"])
  k_c = np.array(coef_data["Coef:MuonAcc_kc"])
  k_w = np.array(coef_data["Coef:MuonAcc_kw"])
  k_c2 = np.array(coef_data["Coef:MuonAcc_kc2"])
  k_w2 = np.array(coef_data["Coef:MuonAcc_kw2"])
  k_cw = np.array(coef_data["Coef:MuonAcc_kcw"])
  
  return muon_acc_factor(k_0, k_c, k_w, k_c2, k_w2, k_cw, delta_c, delta_w)

# ------------------------------------------------------------------------------

class SingleCutTest:
  """ Class for everything needed to test a single cut value.
  """
  
  def __init__(self, rdf, cut_val, delta_c, delta_w, costh_branch, distr_name, coords):
    rdf_filtered = rdf.Filter(SMA.get_ndim_costh_cut(cut_val, delta_c, delta_w, costh_branch))
    cut_distr_name = "{}_dc{}_dw{}".format(distr_name, delta_c, delta_w)
    self.hist_cut_ptr = DH.get_hist_ptr(rdf_filtered, cut_distr_name, coords)
    self.hist_cut = None
    self.hist_par = None
    
    self.delta_c = delta_c # Cut values
    self.delta_w = delta_w
    
  def evaluate(self, coef_data, hist_nocuts):
    """ Evaluates the histograms of the test for both the actual cut and the
        parametrisation of the cut.
        Requires the coefficients and the histogram without cuts to calculate
        the parametrised cut effect.
    """
    self.hist_cut = self.hist_cut_ptr.GetPtr()
    
    self.hist_par = hist_nocuts.Clone()
    self.hist_par.SetName("{}_par".format(self.hist_cut.GetName()))
    
    # Get the factors that describe the result of the parametrisation
    factors = binned_muon_acc_factors(coef_data, self.delta_c, self.delta_w)
    
    i = 0 # bin index not including under/over-flow
    for bin in DH.get_bin_range(self.hist_cut):
      # Skip overflow and underflow bins
      if self.hist_cut.IsBinUnderflow(bin) or self.hist_cut.IsBinOverflow(bin): 
        continue
      
      # Determine the factor for the bin (caused by the cut)  
      factor = factors[i]
      if factor > 1:
        factor = 1
      elif factor < 0:
        factor = 0
    
      # Scale the current bin 
      self.hist_par.SetBinContent(bin, factor*self.hist_par.GetBinContent(bin))
      i += 1 # Increment bin index without under/over-flow

# ------------------------------------------------------------------------------

class MuonAccValidator:
  """ Class that performs tests of the validity of the muon acceptance 
      parametrisation.
  """
  
  def __init__(self, rdf, cut_val, delta, costh_branch, distr_name, coords):
    """ Essentially the same as muon acceptance calculation itself, uses way 
        more points to test.
    """
    self.cut_val = cut_val
    self.delta = delta
    self.distr_name = distr_name
    self.coords = coords
    
    # Need branch(es) as array, and allow passing as string
    if isinstance(costh_branch, str):
      costh_branch = [costh_branch]
    
    # Delta-center, Delta-width combinations to test
    self.dc_tests = [-4, -2, -1, -0.5, 0, 0.5, 1, 2, 4]
    self.dw_tests = [-4, -2, -1, -0.5, 0, 0.5, 1, 2, 4]
    self.d_max = 4 # Maximum dc+dw value that will be tested
    self.test_vals = []
    for dc in self.dc_tests:
      for dw in self.dw_tests:
        if np.sqrt(dc**2+dw**2) > self.d_max+0.001:
          continue
        else:
          self.test_vals.append([dc*delta,dw*delta])
        
    # Set up tests
    self.tests = [SingleCutTest(rdf, cut_val, delta_c, delta_w, costh_branch, distr_name, coords) for delta_c, delta_w in self.test_vals]
    self.histptr_nocut =  DH.get_hist_ptr(rdf, distr_name + "_nocut_val", coords)

  def write_validation_data(self, coef_data, output, base_name, metadata, 
                            n_total, cross_section):
    """ Write the histogram data for all the validation histograms to the 
        output directory.
    """
    hist_nocuts = self.histptr_nocut.GetPtr()
    dim = hist_nocuts.GetDimension()
      
    # Find the histogram that has the cut without deviations
    hist_0_arr = [test for test in self.tests if (test.delta_c == 0 and test.delta_w == 0)]
    if not len(hist_0_arr) == 1:
      raise ValueError("Didn't find exactly one zero-cut array, found {}".format(len(hist_0_arr)))
    hist_0 = hist_0_arr[0].hist_cut_ptr.GetPtr()
    
    # Get the bin_indices without under/overflow bins:
    bin_range = DH.get_bin_range(hist_nocuts)
    n_bins = len(bin_range)
    
    # --- Determine the csv data for validation --------------------------------
    
    # Create the dictionary for the validation data
    val_data = {
      "Delta-c" : [],
      "Delta-w" : []
    }
    for i_bin in range(n_bins):
      val_data["C{}".format(i_bin)] = [] # Value with true cut
      val_data["P{}".format(i_bin)] = [] # Value from parametrisation
    
    # Get the data from all the tested histograms
    for test in self.tests:
      # Evaluate the test histograms
      test.evaluate(coef_data, hist_nocuts)
      
      # Save the tested values
      val_data["Delta-c"].append(test.delta_c)
      val_data["Delta-w"].append(test.delta_w)
      
      # Get all the bin values from the histogram
      for i_bin in range(n_bins):
        bin = bin_range[i_bin] # Histogram-internal bin index
        val_data["C{}".format(i_bin)].append(test.hist_cut.GetBinContent(bin) ) # Value with true cut
        val_data["P{}".format(i_bin)].append(test.hist_par.GetBinContent(bin) ) # Value from parametrisation
      
    # Create a pandas dataframe
    df = pd.DataFrame(val_data)

    # Write the dataframe to a csv file
    val_subdir = "{}/validation".format(output.dir)
    OH.create_dir(val_subdir)
    file_path = "{}/{}_valdata.csv".format(val_subdir,base_name)
    df.to_csv(file_path)

    # --- Determine all the needed metadata ------------------------------------
    
    # Get the coordinate infos
    coord_names = [coord.name for coord in self.coords]
    coord_nbins = [coord.n_bins for coord in self.coords]
    coord_mins = [coord.min for coord in self.coords]
    coord_maxs = [coord.max for coord in self.coords]
    
    # Get the data for the histogram without any cut
    nocut_data = [hist_nocuts.GetBinContent(bin) for bin in bin_range]
    
    # Determine the bin centers
    bin_centers = []
    for bin in bin_range:
      # Find the axis-specific bin indices
      bin_xyz = [ctypes.c_int(0) for d in range(3)]
      hist_0.GetBinXYZ(bin,bin_xyz[0],bin_xyz[1],bin_xyz[2])
      bin_xyz = [int(bin_d.value) for bin_d in bin_xyz]
          
      # Find the bin center value for each axis
      bin_center = [hist_0.GetXaxis().GetBinCenter(bin_xyz[0])]
      if dim > 1: 
        bin_center.append(hist_0.GetYaxis().GetBinCenter(bin_xyz[1]))
      if dim > 2:
        bin_center.append(hist_0.GetZaxis().GetBinCenter(bin_xyz[2]))
      bin_centers.append(bin_center)

    # Attach metadata to beginning of file
    val_metadata = CSVM.CSVMetadata()
    val_metadata.metadata = metadata.metadata.copy()
    val_metadata["NTotalMC"] = n_total
    val_metadata["CrossSection"] = cross_section
    val_metadata["CoordName"] = coord_names
    val_metadata["CoordNBins"] = coord_nbins
    val_metadata["CoordMin"] = coord_mins
    val_metadata["CoordMax"] = coord_maxs
    val_metadata["BinCenters"] = bin_centers
    val_metadata["NoCutData"] = nocut_data
    val_metadata["Delta"] = self.delta

    # Attach the metadata to the data file
    val_metadata.write(file_path)

# ------------------------------------------------------------------------------
