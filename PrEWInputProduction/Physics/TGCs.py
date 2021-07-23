import logging as log
import numpy as np
import ROOT
import scipy.optimize as opt
import sys
from tqdm import tqdm

# Local modules
sys.path.append("../IO")
import OutputHelpers as OH
import TGCConfigReader as ITCR
sys.path.append("../ROOTHelp")
import DistrHelpers as DH
  
# ------------------------------------------------------------------------------

def TGC_factor(TGC_dev, k_g, k_k, k_l, k_g2, k_k2, k_l2, k_gk, k_gl, k_kl):
  """ Return the factor by which a bin needs to be multiplied, given all the 
      needed coefficients and the TGC deviations.
      TGC_dev -> delta g1z, delta kappa_gamma, delta lambda_gamma
  """
  dg, dk, dl = np.transpose(TGC_dev)
  return 1.0 \
         + k_g * dg + k_k * dk + k_l * dl \
         + k_g2 * dg**2 + k_k2 * dk**2 + k_l2 * dl**2 \
         + k_gk * dg * dk + k_gl * dg * dl + k_kl * dk * dl
         
# ------------------------------------------------------------------------------
  
def get_init_coef_guess(TGC_dev_points, R):
  """ Get an initial guess for the 9 coefficients of the TGC polynomial,
      using 9 deviation points and solving the linear system.
  """
  if len(TGC_dev_points) != 9:
    raise Exception("Need exactly 9 points")
    
  dg = TGC_dev_points[:,0]
  dk = TGC_dev_points[:,1]
  dl = TGC_dev_points[:,2]
  
  # Calculate the polynomial points (compare "TGC_factor" function)
  pol_point_arr = np.stack([ dg, dk, dl,
                             dg**2, dk**2, dl**2,
                             dg * dk, dg * dl, dk * dl ], axis=1)
  
  return np.linalg.solve(pol_point_arr, R-1.0)
  
  
def get_fitted_coefs(TGC_dev_points, R, sigma):
  """ Perform fit to extract the coefficients of the 3D quadratic polynomial
      using a wider array of points:
      - First get an initial estimate for the coef's by solving the exact 
        equation system for the first 9 point
      - First try to estimate an uncertainty on the bin values using the 
        MC statistics uncertainty
      - Check if that leads to a good initial chi^2, if not scale the 
        uncertainties
      - Then perform fit using all points
      Needs:
        TGC_dev_points ... TGC deviation points (d g1z, d ka, d la)
        R ... ration wrt. SM at each point
        sigma ... estimation of uncertainty on R at each point
  """
  TGC_dev_points = np.array(TGC_dev_points)
  R = np.array(R)
  sigma = np.array(sigma)
  
  # Solve linear equation system for first 9 points to get intial coefs
  coefs_ini = get_init_coef_guess(TGC_dev_points[:9], R[:9])
  
  # Determine fit starting point
  R_prefit = TGC_factor(TGC_dev_points, *coefs_ini) # * converts array to args
      
  # Perform fit
  coefs, cov = opt.curve_fit(TGC_factor, TGC_dev_points, R, sigma=sigma, p0=coefs_ini)
  return coefs

# ------------------------------------------------------------------------------

def get_coef_data(hist_SM, hists_dev, TGC_dev_points):
  """ Calculate all the coefficients and return them in a dictionary that can be
      written out by pandas into CSV.
      A two step approach is used:
        1. Six specific cuts are used to solve the linear equations for a first
           estimate of the coefficients.
        2. Using the first estimates as starting values, and a larger number of
           cuts, a fit is performed to get more accurate coefficients.
      Seven histograms are needed for the first step:
        - original without any cut at all
        - 6 histograms with cuts at predetermined points to determine the
          polynomial coefficients.
  """
  coefs = []
  
  # Doing this in loop instead of with TH1-operators to control each case
  bin_range = DH.get_bin_range(hist_SM)
  insufficient_MC_bins = 0 # Count the number of bins w/ insufficient MC
  for bin in tqdm(bin_range, desc="Calculate TGC coef's"):
    # Skip overflow and underflow bins
    if hist_SM.IsBinUnderflow(bin) or hist_SM.IsBinOverflow(bin): 
      continue
      
    N_SM = hist_SM.GetBinContent(bin)
    
    # Check that there's at least one event
    if (N_SM < 0.5):
      bin_coefs = np.zeros(9)
      if coefs:
        coefs.append(bin_coefs)
      else:
        coefs = [bin_coefs]
      insufficient_MC_bins += 1
      continue 
      
    # Ratios in this bin for each histogram (with different cut points)
    R = np.array([float(hist.GetBinContent(bin)) / N_SM for hist in hists_dev])
    
    # Estimate the uncertainty on the ratio
    bin_unc = lambda hist: np.sqrt(float(hist.GetBinError(bin)**2 - hist.GetBinContent(bin)**2/N_SM) / (N_SM * (N_SM-1)))
    sigma = np.array([bin_unc(hist) if N_SM > 1 else float(hist.GetBinError(bin)) for hist in hists_dev])
    
    # Extract the coefficients
    bin_coefs = get_fitted_coefs(TGC_dev_points, R, sigma)
    
    if coefs:
      coefs.append(bin_coefs)
    else:
      coefs = [bin_coefs]

  if (insufficient_MC_bins > 0):
    log.info("Had to skip {} bins due to insufficient MC.".format(insufficient_MC_bins))

  coef_base = "TGC"
  coef_names = ["k_g","k_k","k_l","k_g2","k_k2","k_l2","k_gk","k_gl","k_kl"]
  coef_dict = {}
  coefs = np.array(coefs)
  for c in range(len(coef_names)):
    coef_name = "{}_{}".format(coef_base, coef_names[c])
    coef_dict[coef_name] = coefs[:,c]
  
  return coef_dict
  
# ------------------------------------------------------------------------------

class TGCParametrisation:
  """ Class for determining the coefficients of the TGC parametrisation in each
      bin of a distribution.
  """
  
  def __init__(self, rdf, coords, TGC_config_path, TGC_points_path, distr_name, 
               w_branch_base):
    """ Constructor takes:
         rdf : RDataFrame that hold all events
         coords : coordinates of the n-dimensional distribution
         TGC_config_path : path to the TGC config that contains the dev. scale
         TGC_points_path : path to the file that contains the TGC dev. points
         distr_name : name of the distribution
         w_branch_base : base of the weight branches
    """
    # Ignore any events with 0 weights 
    # (here test by 0.01 because only small deviations are tested so all weights
    #  will be around 1)
    rdf_trimmed = rdf.Filter("{}1 > 0.01".format(w_branch_base))
    
    # Histogram for the Standard Model case
    self.histptr_SM =  DH.get_hist_ptr(rdf_trimmed, distr_name + "_SM", coords)

    # Read the TGC configuration file
    tcr = ITCR.TGCConfigReader(TGC_config_path, TGC_points_path)
    self.TGC_dev_points = tcr.scale * tcr.dev_points
    
    # Create the histograms for each TGC deviation point
    ROOT.TH1.SetDefaultSumw2() # Make sure the weight square errors are tracked
    self.histptrs_dev = []
    for p in range(len(self.TGC_dev_points)):
      w_branch = "{}{}".format(w_branch_base, p)
      self.histptrs_dev.append( 
        DH.get_hist_ptr(rdf_trimmed, 
                        distr_name + "_TGC_dev_".format(p), coords, w_branch) )
  
  def add_coefs_to_data(self, distr_data):
    """ Parametrisation uses 2nd order polynomial approach for 2 parameters.
        Details are not described here (probably in PrEW, else in thesis).
        Coefficients are added to data.
    """
    hist_SM = self.histptr_SM.GetValue()
    hists_dev = [histptr.GetValue() for histptr in self.histptrs_dev]
    
    coef_data = get_coef_data(hist_SM, hists_dev, self.TGC_dev_points)
    
    for coef_name, coefs in coef_data.items():
        distr_data["Coef:{}".format(coef_name)] = coefs
    
    return distr_data

# ------------------------------------------------------------------------------
