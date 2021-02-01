# ------------------------------------------------------------------------------

""" Code to validate the Muon acceptance parametrisation.
"""

# ------------------------------------------------------------------------------

from array import array
import ctypes
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

class SingleBinTest:
  """ Class that for the calculation of validation measures for a single 
      N-dimensional bin.
  """
  
  def __init__(self, bin_center, val_cut, val_par, val_cut0):
    """ val_cut  -> True influence of this cut
        val_par  -> Influence as taken from the parametrisation
        val_cut0 -> Value for the cut without varying the edges
    """
    self.bin_center = bin_center
    self.val_cut = val_cut
    self.val_par = val_par
    self.val_cut0 = val_cut0
        
  def relative_deviation(self):
    """ Return the relative deviation caused by the parametrisation.
    """
    return (self.val_par - self.val_cut) / self.val_cut if self.val_cut > 0 else 0
    
  def deviation_significance(self):
    """ Return the (Poissonian) significance of deviation caused by the 
        parametrisation.
    """
    return abs(self.val_par - self.val_cut) / np.sqrt(self.val_cut) if abs(self.val_cut) > 0 else 0
    
  def deviation_relevance(self):
    """ Return the relevance of the deviation caused by the parametrisation.
        Defined as the deviation relative to the cut-change.
    """        
    return (self.val_par - self.val_cut) / (self.val_cut - self.val_cut0) if abs(self.val_cut - self.val_cut0) > 0 else 0

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
    self.dim = len(coords)

    self.delta_c = delta_c # Cut values
    self.delta_w = delta_w
    
    self.bin_tests = []

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
    
  def prepare_bin_tests(self, hist_cut0, sig_scale):
    """ Prepare the needed measures by creating bin tests for every histogram 
        bin.
        hist_cut0 -> Histogram for cut without edge varying
        sig_scale -> Scale applied to histogram values to get a useful lumi
    """
    for bin in range(hist_cut0.GetNcells()):
      # Skip overflow and underflow bins
      if hist_cut0.IsBinUnderflow(bin) or hist_cut0.IsBinOverflow(bin): 
          continue
          
      # Find the axis-specific bin indices
      bin_xyz = [ctypes.c_int(0) for d in range(3)]
      hist_cut0.GetBinXYZ(bin,bin_xyz[0],bin_xyz[1],bin_xyz[2])
      bin_xyz = [int(bin_d.value) for bin_d in bin_xyz]
          
      # Find the bin center value for each axis
      bin_center = []
      bin_center.append(hist_cut0.GetXaxis().GetBinCenter(bin_xyz[0]))
      if self.dim > 1: 
        bin_center.append(hist_cut0.GetYaxis().GetBinCenter(bin_xyz[1]))
      if self.dim > 2:
        bin_center.append(hist_cut0.GetZaxis().GetBinCenter(bin_xyz[2]))
        
      # Find all relevant result values
      val_cut = self.hist_cut.GetBinContent(bin) * sig_scale
      val_par = self.hist_par.GetBinContent(bin) * sig_scale
      val_cut0 = hist_cut0.GetBinContent(bin) * sig_scale
      self.bin_tests.append(SingleBinTest(np.array(bin_center), val_cut, val_par, val_cut0))
      
    self.bin_tests = np.array(self.bin_tests)
    
  def get_axis_graphs(self, axis):
    """ Get the validation graphs for the given axis.
    """
    # Collect all the measures together with the relevant axis coordinate
    # (Use explicit double arrays that ROOT can understand)
    x = array('d')
    y_dev = array('d')
    y_sig = array('d')
    y_rel = array('d')
    for bin_test in self.bin_tests:
      x.append(bin_test.bin_center[axis])
      y_dev.append(bin_test.relative_deviation())
      y_sig.append(bin_test.deviation_significance())
      y_rel.append(bin_test.deviation_relevance())
    
    # Create the graphs that test the mistake made by the parametrisation
    base_name = self.hist_cut.GetName()
    
    graph_dev = ROOT.TGraph(len(self.bin_tests), x, y_dev)
    graph_dev.SetName("{}_g_dev".format(base_name))
    graph_sig = ROOT.TGraph(len(self.bin_tests), x, y_sig)
    graph_sig.SetName("{}_g_sig".format(base_name))
    graph_rel = ROOT.TGraph(len(self.bin_tests), x, y_rel)
    graph_rel.SetName("{}_g_rel".format(base_name))
    
    return { "dev": graph_dev, "sig": graph_sig, "rel": graph_rel }
    
  def get_all_measures(self):
    """ Get the arrays with all the values for the measures for all the bins.
    """
    return {
      "dev": np.array([test.relative_deviation() for test in self.bin_tests]),
      "sig": np.array([test.deviation_significance() for test in self.bin_tests]),
      "rel": np.array([test.deviation_relevance() for test in self.bin_tests]) }
      
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
      
    # Find the histogram that has the cut without deviations
    hist_0_arr = [test for test in self.tests if (test.delta_c == 0 and test.delta_w == 0)]
    if not len(hist_0_arr) == 1:
      raise ValueError("Didn't find exactly one zero-cut array, found {}".format(len(hist_0_arr)))
    hist_0 = hist_0_arr[0].hist_cut_ptr.GetPtr()
    
    # Evaluate all the tests
    for test in self.tests:
      test.evaluate(coef_data, hist_nocuts)
      test.prepare_bin_tests(hist_0, sig_scale)
      
    # --------------------------------------------------------------------------
    # Plotting of deviations for each axis

    for d in range(len(self.coords)):
      coord_name = self.coords[d].name

      # Create the stacks for the result checks
      stack_name_base = "{}_{}".format(base_name, coord_name)
      stack_name_dev = "{}_dev".format(stack_name_base)
      stack_name_sig = "{}_sig".format(stack_name_base)
      stack_name_rel = "{}_rel".format(stack_name_base)
      
      stack_dev = ROOT.TMultiGraph(stack_name_dev, stack_name_dev)
      stack_sig = ROOT.TMultiGraph(stack_name_sig, stack_name_sig)
      stack_rel = ROOT.TMultiGraph(stack_name_rel, stack_name_rel)
    
      # Get all the individual graphs for the different checked cut points
      for test in self.tests:
        test_graphs = test.get_axis_graphs(d)
        graph_dev = test_graphs["dev"]
        graph_sig = test_graphs["sig"]
        graph_rel = test_graphs["rel"]
        
        color = self.get_color_index(test.delta_c,test.delta_w)
        graph_dev.SetMarkerColor(color)
        graph_sig.SetMarkerColor(color)
        graph_rel.SetMarkerColor(color)
        
        stack_dev.Add(graph_dev)
        stack_sig.Add(graph_sig)
        stack_rel.Add(graph_rel)
        
      # Draw and save the stacks
      canvas_dev = ROOT.TCanvas("c_{}".format(stack_name_dev))
      canvas_dev.cd()
      stack_dev.Draw("AP")
      stack_dev.GetXaxis().SetTitle(coord_name)
      stack_dev.GetYaxis().SetTitle("(N_{param}-N_{cut})/N_{cut}")
      
      canvas_sig = ROOT.TCanvas("c_{}".format(stack_name_sig))
      canvas_sig.cd()
      stack_sig.Draw("AP")
      stack_sig.GetXaxis().SetTitle(coord_name)
      stack_sig.GetYaxis().SetTitle("|N_{param}-N_{cut}|/#sqrt{N_{cut}}")
      
      canvas_rel = ROOT.TCanvas("c_{}".format(stack_name_rel))
      canvas_rel.cd()
      stack_rel.Draw("AP")
      stack_rel.GetXaxis().SetTitle(coord_name)
      stack_rel.GetYaxis().SetTitle("(N_{param}-N_{cut})/(N_{cut}-N_{cut,0})")
      
      for extension in extensions:
        # Create the plot subdirectory
        plot_subdir = "{}/plots/{}".format(output.dir,extension)
        OH.create_dir(plot_subdir)
        
        # Save the histograms
        canvas_dev.Print("{}/{}.{}".format(plot_subdir, stack_name_dev, extension))
        canvas_sig.Print("{}/{}.{}".format(plot_subdir, stack_name_sig, extension))
        canvas_rel.Print("{}/{}.{}".format(plot_subdir, stack_name_rel, extension))
        
    # --------------------------------------------------------------------------
    # Plotting of overall distribution of deviations  
        
    # Arrays to track 1D distribution of deviations depending on the test radius
    r_steps = [ 0.0, 0.75, 1.5, 3.0, 5.5]
    r_colors = [self.get_color_index(r*self.delta,0) for r in [0.5, np.sqrt(2), 2.5, 5]]
    vals_sig = [[] for r in range(len(r_steps)-1)] # deviation-significance
    vals_rel = [[] for r in range(len(r_steps)-1)] # deviation-relevance

    # Collect and correctly sort the validation measure values of all bins
    for test in self.tests:
      # Find the right radius-index to store the deviations in
      i_r = None
      d_tot = self.get_d_norm(test.delta_c, test.delta_w) * self.d_max
      for s in range(len(r_steps)-1):
        if (d_tot >= r_steps[s]) and (d_tot < r_steps[s+1]):
          i_r = s
          break
      
      # Collect all the validation measures
      # -> Skip 0-values, happen only if no cut influence or no deviation from 
      #    cut-change
      test_dict = test.get_all_measures()
      for sig in test_dict["sig"]:
        if sig != 0:
          vals_sig[i_r].append(sig)
        
      for rel in test_dict["rel"]:
        if rel != 0:
          vals_rel[i_r].append(rel)
          
    # Create a stacks for the 1D histograms of the deviation
    stack_name_rel = "{}_rel".format(base_name)
    stack_name_sig = "{}_sig".format(base_name)
    
    stack_rel_1D = ROOT.THStack(stack_name_rel, stack_name_rel)
    legend_rel_1D = ROOT.TLegend(0.2,0.4,0.5,0.9)
    legend_rel_1D.SetHeader("Test val. in #Delta = {}".format(self.delta))
    
    stack_sig_1D = ROOT.THStack(stack_name_sig, stack_name_sig)
    legend_sig_1D = ROOT.TLegend(0.5,0.4,0.9,0.9)
    legend_sig_1D.SetHeader("Test val. in #Delta = {}".format(self.delta))
    
    # Plot the deviation-relevance distribution for each step in test-radius
    for s in range(len(r_steps)-1):
      r_min = r_steps[s]
      r_max = r_steps[s+1]
      step_label = "{} - {}".format(r_min, r_max)
      
      # Create the deviation histograms for this radius range
      hist_name_rel = stack_name_rel + "_" + str(r_min) + "_" + str(r_max)
      new_hist_rel = ROOT.TH1D(hist_name_rel,hist_name_rel,51,-2.5,2.5)
      
      hist_name_sig = stack_name_sig + "_" + str(r_min) + "_" + str(r_max)
      new_hist_sig = ROOT.TH1D(hist_name_sig,hist_name_sig,60,0.0,1.5)
      
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
    canvas_rel_1D = ROOT.TCanvas("c_{}".format(stack_name_rel))
    canvas_rel_1D.cd()
    stack_rel_1D.Draw("nostack")
    stack_rel_1D.GetXaxis().SetTitle("(N_{param}-N_{cut})/(N_{cut}-N_{cut,0})")
    stack_rel_1D.GetYaxis().SetTitle("a.u.")
    stack_rel_1D.SetMinimum(0.0)
    stack_rel_1D.SetMaximum(1.0)
    legend_rel_1D.Draw()
    legend_rel_1D.SetFillStyle(0) # Transparent legend-background
    
    canvas_sig_1D = ROOT.TCanvas("c_{}".format(stack_name_sig))
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
      canvas_rel_1D.Print("{}/{}.{}".format(plot_subdir, stack_name_rel, extension))
      canvas_sig_1D.Print("{}/{}.{}".format(plot_subdir, stack_name_sig, extension))

# ------------------------------------------------------------------------------