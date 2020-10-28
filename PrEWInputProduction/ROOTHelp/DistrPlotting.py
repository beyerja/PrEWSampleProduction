import ROOT

# ------------------------------------------------------------------------------

""" Helper classes and functions for plotting ROOT histograms.
"""

# ------------------------------------------------------------------------------

def draw_hist(hist, output, hist_name, extensions=["pdf","root"]):
    # Draw the histogram
    canvas = ROOT.TCanvas("c_{}".format(output.distr_name))
    canvas.cd()
    
    # Draw option dependent on dimensionality
    draw_opt = ""
    dim = hist.GetDimension()
    if dim == 1:
      draw_opt = "hist"
    if dim == 2:
      draw_opt = "colz"
    if dim == 3:
     draw_opt = "box2"
    
    hist.Draw(draw_opt)

    # Save the histogram
    plot_output_base = "{}/plots/{}".format(output.dir, hist_name)
    for extension in extensions:
      canvas.Print("{}.{}".format(plot_output_base, extension))

# ------------------------------------------------------------------------------
