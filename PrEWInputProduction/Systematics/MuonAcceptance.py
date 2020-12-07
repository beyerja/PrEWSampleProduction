import logging as log
import numpy as np
import ROOT
import sys
from tqdm import tqdm

sys.path.append("../ROOTHelp")
import DistrHelpers as DH

# ------------------------------------------------------------------------------

def get_costh_cut(cut_val, center_shift, width_shift, costh_branch):
  """ Get the string that describes the cos(theta) cut for the given cut values.
      Four inputs are needed:
        The central cut value (same for both sides +-).
        The change that of the acceptance center (center_shift).
        The change that of the acceptance width (width_shift).
        The name of the cos(Theta) branch.
  """
  pos_cut =   abs(cut_val) + center_shift + width_shift
  neg_cut = - abs(cut_val) + center_shift - width_shift  
  cut_str = "({} > {}) && ({} < {})".format(costh_branch, neg_cut, costh_branch,
                                            pos_cut)
  return cut_str

def get_ndim_costh_cut(cut_val, center_shift, width_shift, costh_branches):
  """ Applying the same cos(theta) cut to multiple branches (/particles) at the
      same time. 
  """
  cut_str = ""
  for costh_branch in costh_branches:
    if cut_str != "":
      cut_str += " && "  
    cut_str += get_costh_cut(cut_val, center_shift, width_shift, costh_branch)
  return cut_str
  
# ------------------------------------------------------------------------------

def get_coef_data(hist_nocut, hist_0, hist_1, hist_2, hist_3, hist_4, hist_5, 
                  delta):
  """ Calculate all the coefficients and return them in a dictionary that can be
      written out by pandas into CSV.
      Seven histograms are needed:
        - original without any cut at all
        - 6 histograms with cuts at predetermined points to determine the
          polynomial coefficients.
      The points:
        # | delta_c [delta] | delta_w [delta]
        0 |  0              |  0
        1 |  0              |  2
        2 |  0              | -2
        3 |  0.5            |  2
        4 | -0.5            | -2
        5 |  1              | -2 
      In addition, the value for delta is needed.
  """
  cut_hists = [hist_0, hist_1, hist_2, hist_3, hist_4, hist_5]
  
  # Coefficients to collect:
  k_0 = []
  k_c = []
  k_w = []
  k_c2 = []
  k_w2 = []
  k_cw = []
  
  # Doing this in loop instead of with TH1-operators to control each case
  bin_range = DH.get_bin_range(hist_nocut)
  insufficient_MC_bins = 0 # Count the number of bins w/ insufficient MC
  for bin in tqdm(bin_range, desc="Calculate muon acc. coefs"):
    # Skip overflow and underflow bins
    if hist_nocut.IsBinUnderflow(bin) or hist_nocut.IsBinOverflow(bin): 
      continue
      
    N_nocut = hist_nocut.GetBinContent(bin)
    if (N_nocut < 3.5):
      # Got too few MC events to say anything about the behaviour
      k_0.append(1.0) # Constant term 1, all other 0
      for k in [k_c, k_w, k_c2, k_w2, k_cw]:
        k.append(0.0)
      insufficient_MC_bins += 1
      continue 
    
    # Ratios in this bin for each histogram (with different cut points)
    R = np.array([float(hist.GetBinContent(bin)) / N_nocut for hist in cut_hists])
    
    # Actual calculation of the coefficients
    k_0.append(R[0])
    k_c.append( 1.0/delta * ( - R[1] + R[2] + R[3] - R[4]) )
    k_w.append( 1.0/(4.0*delta) * ( R[1] - R[2] ) )
    k_c2.append( 2.0/(3.0*delta**2) * ( -3.0 * R[2] + 2.0 * R[4] + R[5]) )
    k_w2.append( 1.0/(8.0*delta**2) * ( -2.0 * R[0] + R[1] + R[2]) )
    k_cw.append( 1.0/delta**2 * (-1.0/2.0 * R[1] + 1.0/2.0 * R[3] + 1.0/6.0 * R[4] - 1.0/6.0 * R[5]) )

  if (insufficient_MC_bins > 0):
    log.info("Had to skip {} bins due to insufficient MC.".format(insufficient_MC_bins))

  return {"MuonAcc_k0": k_0, 
          "MuonAcc_kc": k_c, "MuonAcc_kw": k_w, 
          "MuonAcc_kc2": k_c2, "MuonAcc_kw2": k_w2, "MuonAcc_kcw": k_cw}

# ------------------------------------------------------------------------------

class MuonAccParametrisation:
  """ Class that can calculate the coefficients required in the parametrisation 
      of the muon acceptance. 
      Muon acceptance is here defined as a simple box acceptance with the same
      cut value on both sides.
      For the parametrisation both sides are varied either 
        - by keeping the acceptance width constant and shifting the center 
          (center_shift) or 
        - by keeping the center constant and changing the width (width_shift).
  """
  
  def __init__(self, rdf, cut_val, delta, costh_branch, distr_name, coords):
    """ Takes four cut-related inputs:
          The dataframe that can be used to extract the changes with the cuts.
          The initial cut value which is the same on both side (+-cos(theta)).
          The deviation that is used in the test to find the cut-dependence.
          The name of the cos(Theta_muon) branch (can be string or array).
        And two histogram-related input (name and coordinate information).
    """
    self.cut_val = cut_val
    self.delta = delta
    
    # Need branch(es) as array, and allow passing as string
    if isinstance(costh_branch, str):
      costh_branch = [costh_branch]
    
    # Five different cuts are tested 
    rdf_0 =  rdf.Filter(get_ndim_costh_cut(cut_val, 0, 0, costh_branch))
    rdf_1 =  rdf.Filter(get_ndim_costh_cut(cut_val, 0, 2.0*delta, costh_branch))
    rdf_2 =  rdf.Filter(get_ndim_costh_cut(cut_val, 0, -2.0*delta, costh_branch))
    rdf_3 =  rdf.Filter(get_ndim_costh_cut(cut_val, 0.5*delta, 2.0*delta, costh_branch))
    rdf_4 =  rdf.Filter(get_ndim_costh_cut(cut_val, -0.5*delta, -2.0*delta, costh_branch))
    rdf_5 =  rdf.Filter(get_ndim_costh_cut(cut_val, delta, -2.0*delta, costh_branch))
  
    self.histptr_nocut =  DH.get_hist_ptr(rdf, distr_name + "_nocut", coords)
    self.histptr_0 = DH.get_hist_ptr(rdf_0, distr_name + "_0", coords)
    self.histptr_1 = DH.get_hist_ptr(rdf_1, distr_name + "_1", coords)
    self.histptr_2 = DH.get_hist_ptr(rdf_2, distr_name + "_2", coords)
    self.histptr_3 = DH.get_hist_ptr(rdf_3, distr_name + "_3", coords)
    self.histptr_4 = DH.get_hist_ptr(rdf_4, distr_name + "_4", coords)
    self.histptr_5 = DH.get_hist_ptr(rdf_5, distr_name + "_5", coords)
  
  def add_coefs_to_data(self, distr_data):
    """ Parametrisation uses 2nd order polynomial approach for 2 parameters.
        Details are not described here (probably in PrEW, else in thesis).
        Coefficients are added to data.
    """
    hist_nocut = self.histptr_nocut.GetValue()
    hist_0 = self.histptr_0.GetValue()
    hist_1 = self.histptr_1.GetValue()
    hist_2 = self.histptr_2.GetValue()
    hist_3 = self.histptr_3.GetValue()
    hist_4 = self.histptr_4.GetValue()
    hist_5 = self.histptr_5.GetValue()
    
    coef_data = get_coef_data(hist_nocut, hist_0, hist_1, hist_2, hist_3, 
                              hist_4, hist_5, self.delta)
    
    for coef_name, coefs in coef_data.items():
        distr_data["Coef:{}".format(coef_name)] = coefs
    
    return distr_data
    
  def add_coefs_to_metadata(self, metadata):
    """ Add the needed global coefficients to the metadata.
    """
    metadata.add_coef("MuonAcc","CutValue",self.cut_val)
    
# ------------------------------------------------------------------------------

def default_acc_cut():
  """ Define the default acceptance cut for the muon acceptance box.
  """
  return 0.95

def default_delta():
  """ Define the default delta variation used to calculate the cut dependence.
  """
  return 2.0e-4

# ------------------------------------------------------------------------------
