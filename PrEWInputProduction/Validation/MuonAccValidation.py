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
    self.coords = coords
    
    # Need branch(es) as array, and allow passing as string
    if isinstance(costh_branch, str):
      costh_branch = [costh_branch]
    
    # Delta-center, Delta-width combinations to test
    self.dc_tests = [-5, -2.5, -1, -0.5, 0, 0.5, 1, 2.5, 5]
    self.dw_tests = [-5, -2.5, -1, -0.5, 0, 0.5, 1, 2.5, 5]
    self.d_max = 5 # Maximum dc+dw value that will be tested
    self.test_vals = []
    for dc in self.dc_tests:
      for dw in self.dw_tests:
        if np.sqrt(dc**2+dw**2) > self.d_max+0.001:
          continue
        else:
          self.test_vals.append([dc*delta,dw*delta])
        
    # Create the needed ROOT colors
    self.colors = []
    self.create_colors()
    
    # Set up tests
    self.tests = [SingleCutTest(rdf, cut_val, delta_c, delta_w, costh_branch, distr_name, coords) for delta_c, delta_w in self.test_vals]
    self.histptr_nocut =  DH.get_hist_ptr(rdf, distr_name + "_nocut_val", coords)

  def get_d_norm(self, dc, dw):
    """ Get normalized root-of-squares sum of dc and dw.
        Sign is not considered, only absolute deviation from 0.
    """
    d_total = np.sqrt(dc**2+dw**2) / self.delta
    return d_total/self.d_max

  def get_color_index(self, dc, dw):
    """ Translate the devation into a (custom) ROOT color index.
    """
    # Assume there are less than 100 distinct values
    return 9000 + int(1000.0*self.get_d_norm(dc,dw))
    
  def create_colors(self):
    """ Create all the necessary ROOT TColors.
    """
    colormap = cm.get_cmap("plasma") # Get a matplot lib color map
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
    
  def validate(self, coef_data, sig_scale, output, base_name, extensions=["pdf","png","root"]):
    """ Create plots to test the validity of the MuonAcceptance parametrisation 
        and its coefficients.
        Requires a "significance scale" which correctly scales the histograms
        to some luminosity in order to meaningfully assess a significance of the
        mistake made by the parametrisation.
    """

    hist_nocuts = self.histptr_nocut.GetPtr()
    hist_nocuts.Scale(sig_scale)
    if not hist_nocuts.GetDimension() == 1:
      log.error("Validation plots not implemented for histograms with dim != 1")
      return
      
    # Find the histogram that has the cut without deviations
    hist_0_arr = [test for test in self.tests if (test.delta_c == 0 and test.delta_w == 0)]
    if not len(hist_0_arr) == 1:
      raise ValueError("Didn't find exactly one zero-cut array, found {}".format(len(hist_0_arr)))
    hist_0 = hist_0_arr[0].hist_ptr.GetPtr()

    # Create the stacks for the result checks
    stack_name_base = "{}_stack".format(base_name)
    stack_name_diff = "{}_rel_diff".format(stack_name_base)
    stack_name_sig = "{}_sig".format(stack_name_base)
    stack_name_rel = "{}_relevance".format(stack_name_base)

    stack_diff = ROOT.TMultiGraph(stack_name_diff, stack_name_diff)
    stack_sig = ROOT.THStack(stack_name_sig, stack_name_sig)
    stack_rel = ROOT.TMultiGraph(stack_name_rel, stack_name_rel)
    
    # Arrays to track 1D distribution of deviations depending on the test radius
    r_steps = [ 0.0, 0.75, 1.5, 3.0, 5.5]
    r_colors = [self.get_color_index(r*self.delta,0) for r in [0.5, np.sqrt(2), 2.5, 5]]
    vals_sig = [[] for r in range(len(r_steps)-1)] # deviation-significance
    vals_rel = [[] for r in range(len(r_steps)-1)] # deviation-relevance

    for test in self.tests:
      hist = test.hist_ptr.GetPtr()
      hist.Scale(sig_scale)
      
      # Create the histograms that test the mistake made by the parametrisation
      hist_diff = hist_nocuts.Clone()
      hist_diff.SetName("{}_rel_diff".format(hist.GetName()))
      hist_sig = hist_nocuts.Clone()
      hist_sig.SetName("{}_sig".format(hist.GetName()))
      hist_rel = hist_nocuts.Clone()
      hist_rel.SetName("{}_relevance".format(hist.GetName()))
      
      # Get the factors that describe the result of the parametrisation
      factors = binned_muon_acc_factors(coef_data, test.delta_c, test.delta_w)
      
      # Find the right radius-index to store the deviations in
      i_r = None
      d_tot = self.get_d_norm(test.delta_c, test.delta_w) * self.d_max
      for s in range(len(r_steps)-1):
        if (d_tot >= r_steps[s]) and (d_tot < r_steps[s+1]):
          i_r = s
          break
      
      i = 0 # bin index not including under/over-flow
      for bin in DH.get_bin_range(hist):
        # Skip overflow and underflow bins
        if hist.IsBinUnderflow(bin) or hist.IsBinOverflow(bin): 
          continue
        
        # Determine the factor for the bin (caused by the cut)  
        factor = factors[i]
        if factor > 1:
          factor = 1
        elif factor < 0:
          factor = 0
        
        par_content = factor*hist_nocuts.GetBinContent(bin) 
        true_content = hist.GetBinContent(bin)
        cut0_content = hist_0.GetBinContent(bin)
        
        # Determine the relative difference caused by using the parametrisation
        rel_diff = (par_content - true_content) / true_content if true_content > 0 else 0
        hist_diff.SetBinContent(bin, rel_diff)
        
        # Detemine the significance of the difference
        sig = abs(par_content - true_content) / np.sqrt(true_content) if abs(true_content) > 0 else 0
        hist_sig.SetBinContent(bin, sig)
        if true_content - cut0_content != 0:
          vals_sig[i_r].append(sig)
        
        # Determine the relevance of the difference (compared to actual change of cut)
        relevance = (par_content - true_content) / (true_content - cut0_content) if abs(true_content - cut0_content) > 0 else 0
        hist_rel.SetBinContent(bin, relevance)
        if true_content - cut0_content != 0:
          vals_rel[i_r].append(relevance)
        
        i += 1 # Increment bin index without under/over-flow
      
      # Convert histogram to graf (because contains negative values)
      graph_diff = ROOT.TGraph(hist_diff)
      graph_rel = ROOT.TGraph(hist_rel)
      
      color = self.get_color_index(test.delta_c,test.delta_w)
      graph_diff.SetMarkerColor(color)
      hist_sig.SetLineColor(color)
      graph_rel.SetMarkerColor(color)
      
      stack_diff.Add(graph_diff)
      stack_sig.Add(hist_sig, "hist")
      stack_rel.Add(graph_rel)
    
    # Draw and save the stacks
    canvas_diff = ROOT.TCanvas("c_{}".format(stack_name_diff))
    canvas_diff.cd()
    stack_diff.Draw("AP") # Is TMultiGraph, doesn't need "nostack"
    stack_diff.GetXaxis().SetTitle(self.coords[0].name)
    stack_diff.GetYaxis().SetTitle("(N_{param}-N_{cut})/N_{cut}")
    
    canvas_sig = ROOT.TCanvas("c_{}".format(stack_name_sig))
    canvas_sig.cd()
    stack_sig.Draw("nostack")
    stack_sig.GetXaxis().SetTitle(self.coords[0].name)
    stack_sig.GetYaxis().SetTitle("|N_{param}-N_{cut}|/#sqrt{N_{cut}}")
    
    canvas_rel = ROOT.TCanvas("c_{}".format(stack_name_rel))
    canvas_rel.cd()
    stack_rel.Draw("AP")
    stack_rel.GetXaxis().SetTitle(self.coords[0].name)
    stack_rel.GetYaxis().SetTitle("(N_{param}-N_{cut})/(N_{cut}-N_{cut,0})")
    
    # Create a stacks for the 1D histograms of the deviation
    stack_rel_1D = ROOT.THStack(stack_name_rel+"_1D", stack_name_rel+"_1D")
    legend_rel_1D = ROOT.TLegend(0.2,0.4,0.5,0.9)
    legend_rel_1D.SetHeader("Test val. in #Delta = {}".format(self.delta))
    
    stack_sig_1D = ROOT.THStack(stack_name_sig+"_1D", stack_name_sig+"_1D")
    legend_sig_1D = ROOT.TLegend(0.5,0.4,0.9,0.9)
    legend_sig_1D.SetHeader("Test val. in #Delta = {}".format(self.delta))
    
    # Find the minimum and maximum of the deviation measures for plotting
    min_rel = min([min(arr or [0.0]) for arr in vals_rel])
    max_rel = max([max(arr or [0.0]) for arr in vals_rel])
    
    max_sig = max([max(arr or [0.0]) for arr in vals_sig])
    
    # Plot the deviation-relevance distribution for each step in test-radius
    for s in range(len(r_steps)-1):
      r_min = r_steps[s]
      r_max = r_steps[s+1]
      step_label = "{} - {}".format(r_min, r_max)
      
      # Create the deviation histograms for this radius range
      hist_name_rel = stack_name_rel + "_" + str(r_min) + "_" + str(r_max)
      new_hist_rel = ROOT.TH1D(hist_name_rel,hist_name_rel,30,1.05*min_rel,1.05*max_rel)
      
      hist_name_sig = stack_name_sig + "_" + str(r_min) + "_" + str(r_max)
      new_hist_sig = ROOT.TH1D(hist_name_sig,hist_name_sig,30,0.0,1.05*max_sig)
      
      # Fill the deviation histograms
      for val_rel in vals_rel[s]: new_hist_rel.Fill(val_rel)
      for val_sig in vals_sig[s]: new_hist_sig.Fill(val_sig)
        
      # Normalise
      if new_hist_rel.Integral() > 0: new_hist_rel.Scale(1.0/new_hist_rel.Integral()) 
      if new_hist_sig.Integral() > 0: new_hist_sig.Scale(1.0/new_hist_sig.Integral()) 
        
      # Plotting 
      new_hist_rel.SetLineColor(r_colors[s])
      stack_rel_1D.Add(new_hist_rel, "hist")
      legend_rel_1D.AddEntry(new_hist_rel, step_label)
      
      new_hist_sig.SetLineColor(r_colors[s])
      stack_sig_1D.Add(new_hist_sig, "hist")
      legend_sig_1D.AddEntry(new_hist_sig, step_label)
    
    # Plot the 1D deviation distributions
    canvas_rel_1D = ROOT.TCanvas("c_{}_1D".format(stack_name_rel))
    canvas_rel_1D.cd()
    stack_rel_1D.Draw("nostack")
    stack_rel_1D.GetXaxis().SetTitle("(N_{param}-N_{cut})/(N_{cut}-N_{cut,0})")
    stack_rel_1D.GetYaxis().SetTitle("a.u.")
    stack_rel_1D.SetMinimum(0.0)
    stack_rel_1D.SetMaximum(1.0)
    legend_rel_1D.Draw()
    legend_rel_1D.SetFillStyle(0) # Transparent legend-background
    
    canvas_sig_1D = ROOT.TCanvas("c_{}_1D".format(stack_name_sig))
    canvas_sig_1D.cd()
    stack_sig_1D.Draw("nostack")
    stack_sig_1D.GetXaxis().SetTitle("|N_{param}-N_{cut}|/#sqrt{N_{cut}}")
    stack_sig_1D.GetYaxis().SetTitle("a.u.")
    stack_sig_1D.SetMinimum(0.0)
    stack_sig_1D.SetMaximum(1.0)
    legend_sig_1D.Draw()
    legend_sig_1D.SetFillStyle(0) # Transparent legend-background
    
    # Save the histogram
    for extension in extensions:
      # Create the plot subdirectory
      plot_subdir = "{}/plots/{}".format(output.dir,extension)
      OH.create_dir(plot_subdir)
      
      # Save the histograms
      canvas_diff.Print("{}/{}.{}".format(plot_subdir, stack_name_diff, extension))
      canvas_sig.Print("{}/{}.{}".format(plot_subdir, stack_name_sig, extension))
      canvas_rel.Print("{}/{}.{}".format(plot_subdir, stack_name_rel, extension))
      
      canvas_rel_1D.Print("{}/{}_1D.{}".format(plot_subdir, stack_name_rel, extension))
      canvas_sig_1D.Print("{}/{}_1D.{}".format(plot_subdir, stack_name_sig, extension))

# ------------------------------------------------------------------------------