# ------------------------------------------------------------------------------

""" Code to validate the Muon acceptance parametrisation.
"""

# ------------------------------------------------------------------------------

import logging as log
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import numpy as np
import ROOT
import sys

# Local modules
sys.path.append("../IO")
import OutputHelpers as OH
sys.path.append("../ROOTHelp")
import DistrHelpers as DH
import DistrPlotting as DP
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
  """ Storage class for everything needed to test a single cut value.
  """
  
  def __init__(self, rdf, cut_val, delta_c, delta_w, costh_branch, distr_name, coords):
    rdf_filtered = rdf.Filter(SMA.get_ndim_costh_cut(cut_val, delta_c, delta_w, costh_branch))
    cut_distr_name = "{}_dc{}_dw{}".format(distr_name, delta_c, delta_w)
    self.hist_ptr =  DH.get_hist_ptr(rdf_filtered, cut_distr_name, coords)

    self.delta_c = delta_c # Cut values
    self.delta_w = delta_w

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
    
    # Need branch(es) as array, and allow passing as string
    if isinstance(costh_branch, str):
      costh_branch = [costh_branch]
    
    # Delta-center, Delta-width combinations to test
    self.dc_tests = [-5, -3, -1, -0.5, 0, 0.5, 1, 3, 5]
    self.dw_tests = [-5, -3, -1, -0.5, 0, 0.5, 1, 3, 5]
    self.dc_min = np.amin(self.dc_tests)
    self.dc_max = np.amax(self.dc_tests)
    self.dw_min = np.amin(self.dw_tests)
    self.dw_max = np.amax(self.dw_tests)
    self.test_vals = []
    for dc in self.dc_tests:
      for dw in self.dw_tests:
        self.test_vals.append([dc*delta,dw*delta])
        
    # Create the needed ROOT colors
    self.colors = []
    self.create_colors()
    
    # Set up tests
    self.tests = [SingleCutTest(rdf, cut_val, delta_c, delta_w, costh_branch, distr_name, coords) for delta_c, delta_w in self.test_vals]
    self.histptr_nocut =  DH.get_hist_ptr(rdf, distr_name + "_nocut_val", coords)

  def get_d_norm(self, dc, dw):
    """ Get normalized sum of dc and dw.
        Sign is not considered, only absolute deviation from 0.
    """
    d_total = (abs(dc)+abs(dw)) / self.delta
    d_max = np.amax([abs(self.dc_max),abs(self.dc_min)]) + np.amax([abs(self.dw_max),abs(self.dw_min)])
    return d_total/d_max

  def get_color_index(self, dc, dw):
    """ Translate the devation into a (custom) ROOT color index.
    """
    # Assume there are less than 100 distinct values
    return 9000 + int(1000.0*self.get_d_norm(dc,dw))
    
  def create_colors(self):
    """ Create all the necessary ROOT TColors.
    """
    colormap = cm.get_cmap("inferno") # Get a matplot lib color map
    indices = []
    for test_val in self.test_vals:
      c_i = self.get_color_index(test_val[0],test_val[1])
      if c_i in indices: 
        continue # already created
      else:
        indices.append(c_i)
      
      d_norm = self.get_d_norm(test_val[0],test_val[1])
      c_r, c_g, c_b, alpha = colormap(d_norm)
      
      c_name = "NewColor{}".format(c_i)
      self.colors.append(ROOT.TColor(c_i, c_r, c_g, c_b, c_name))
    
  def validate(self, coef_data, output, base_name, extensions=["pdf","root"]):
    """ Create plots to test the validity of the MuonAcceptance parametrisation 
        and its coefficients.
    """

    hist_nocuts = self.histptr_nocut.GetPtr()
    if not hist_nocuts.GetDimension() == 1:
      log.error("Validation plots not implemented for histograms with dim != 1")
      return

    stack_name = "{}_stack".format(base_name)
    canvas = ROOT.TCanvas("c_{}".format(stack_name))
    canvas.cd()
    stack = ROOT.THStack(stack_name, stack_name)

    for test in self.tests:
      hist = test.hist_ptr.GetPtr()
      hist_diff = hist_nocuts.Clone()
      hist_diff.SetName("{}_scaling".format(hist.GetName()))
      factors = binned_muon_acc_factors(coef_data, test.delta_c, test.delta_w)
      
      i = 0 # bin index not including under/over-flow
      for bin in DH.get_bin_range(hist_diff):
        # Skip overflow and underflow bins
        if hist_diff.IsBinUnderflow(bin) or hist_diff.IsBinOverflow(bin): 
          continue
        
        # Determine the factor for the bin (caused by the cut)  
        factor = factors[i]
        if factor > 1:
          factor = 1
        elif factor < 0:
          factor = 0
        
        # Determine the relative difference caused by using the parametrisation
        par_content = factor*hist_nocuts.GetBinContent(bin) 
        true_content = hist.GetBinContent(bin)
        nocut_content = hist_nocuts.GetBinContent(bin)
        
        rel_sig = abs(par_content - true_content) / abs(nocut_content - true_content) if abs(nocut_content - true_content) > 0 else 0
        hist_diff.SetBinContent(bin, rel_sig)
        
        i += 1 # Increment bin index without under/over-flow
      
      hist_diff.SetLineColor(self.get_color_index(test.delta_c,test.delta_w))
      
      stack.Add(hist_diff)
    
    stack.Draw("nostack")
    
    for extension in extensions:
      # Create the plot subdirectory
      plot_subdir = "{}/plots/{}".format(output.dir,extension)
      OH.create_dir(plot_subdir)
      
      # Save the histogram
      canvas.Print("{}/{}.{}".format(plot_subdir, stack_name, extension))

# ------------------------------------------------------------------------------