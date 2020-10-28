import ROOT

# ------------------------------------------------------------------------------

""" General helper classes and functions for the creation of CSV (and other 
    output) files with the distributions.
"""

# ------------------------------------------------------------------------------

class Coordinate:
    """ Coordinate axis class describing properties of axis in its dimension.
    """
    def __init__(self, name, n_bins, min, max):
        self.name = name
        self.n_bins = n_bins
        self.min = min
        self.max = max

# ------------------------------------------------------------------------------

def get_data_1d(root_hist, coords):
    """ Extract data from TH1.
    """
    # Find bin centers and values, skip overflow/underflow bins
    bins_x={"Centers": [], "LowerEdges": [], "UpperEdges": []}
    bin_values=[]
    for x_bin in range(0, root_hist.GetNbinsX()+2):
        bin = root_hist.GetBin(x_bin)
            
        # Skip overflow and underflow bins
        if root_hist.IsBinUnderflow(bin) or root_hist.IsBinOverflow(bin): 
            continue
    
        # Collect bin information and fill into array
        bins_x["Centers"].append(root_hist.GetXaxis().GetBinCenter(x_bin))
        bins_x["LowerEdges"].append(root_hist.GetXaxis().GetBinLowEdge(x_bin))
        bins_x["UpperEdges"].append(root_hist.GetXaxis().GetBinUpEdge(x_bin))
        value = root_hist.GetBinContent(bin)
        bin_values.append(value)
    
    # Store the data in a dictionary for pandas
    data = { "BinCenters:{}".format(coords[0].name): bin_dims[d]["Centers"],
             "BinLow:{}".format(coords[0].name): bin_dims[d]["LowerEdges"],
             "BinUp:{}".format(coords[0].name): bin_dims[d]["UpperEdges"],
             "Cross sections": bin_values }
    
    return data
  
def get_data_2d(root_hist, coords):
    """ Extract data from TH2.
    """
    # Find bin centers and values, skip overflow/underflow bins
    bins_x={"Centers": [], "LowerEdges": [], "UpperEdges": []}
    bins_y={"Centers": [], "LowerEdges": [], "UpperEdges": []}
    bin_values=[]
    for x_bin in range(0, root_hist.GetNbinsX()+2):
        for y_bin in range(0, root_hist.GetNbinsY()+2):
            bin = root_hist.GetBin(x_bin, y_bin)
            
            # Skip overflow and underflow bins
            if root_hist.IsBinUnderflow(bin) or root_hist.IsBinOverflow(bin): 
                continue
        
            # Collect bin information and fill into array
            bins_x["Centers"].append(root_hist.GetXaxis().GetBinCenter(x_bin))
            bins_y["Centers"].append(root_hist.GetYaxis().GetBinCenter(y_bin))
            bins_x["LowerEdges"].append(root_hist.GetXaxis().GetBinLowEdge(x_bin))
            bins_y["LowerEdges"].append(root_hist.GetYaxis().GetBinLowEdge(y_bin))
            bins_x["UpperEdges"].append(root_hist.GetXaxis().GetBinUpEdge(x_bin))
            bins_y["UpperEdges"].append(root_hist.GetYaxis().GetBinUpEdge(y_bin))
            value = root_hist.GetBinContent(bin)
            bin_values.append(value)
    
    # Store the data in a dictionary for pandas
    data = {}
    bin_dims = [bins_x,bins_y]
    for d in range(len(bin_dims)):
        data["BinCenters:{}".format(coords[d].name)] = bin_dims[d]["Centers"]
        data["BinLow:{}".format(coords[d].name)] = bin_dims[d]["LowerEdges"]
        data["BinUp:{}".format(coords[d].name)] = bin_dims[d]["UpperEdges"]
    data["Cross sections"] = bin_values
    
    return data
  
def get_data_3d(root_hist, coords):
    """ Extract data from TH3.
    """
    # Find bin centers and values, skip overflow/underflow bins
    bins_x={"Centers": [], "LowerEdges": [], "UpperEdges": []}
    bins_y={"Centers": [], "LowerEdges": [], "UpperEdges": []}
    bins_z={"Centers": [], "LowerEdges": [], "UpperEdges": []}
    bin_values=[]
    for x_bin in range(0, root_hist.GetNbinsX()+2):
        for y_bin in range(0, root_hist.GetNbinsY()+2):
            for z_bin in range(0, root_hist.GetNbinsZ()+2):
                bin = root_hist.GetBin(x_bin, y_bin, z_bin)
                
                # Skip overflow and underflow bins
                if root_hist.IsBinUnderflow(bin) or root_hist.IsBinOverflow(bin): 
                    continue
            
                # Collect bin information and fill into array
                bins_x["Centers"].append(root_hist.GetXaxis().GetBinCenter(x_bin))
                bins_y["Centers"].append(root_hist.GetYaxis().GetBinCenter(y_bin))
                bins_z["Centers"].append(root_hist.GetZaxis().GetBinCenter(z_bin))
                bins_x["LowerEdges"].append(root_hist.GetXaxis().GetBinLowEdge(x_bin))
                bins_y["LowerEdges"].append(root_hist.GetYaxis().GetBinLowEdge(y_bin))
                bins_z["LowerEdges"].append(root_hist.GetZaxis().GetBinLowEdge(z_bin))
                bins_x["UpperEdges"].append(root_hist.GetXaxis().GetBinUpEdge(x_bin))
                bins_y["UpperEdges"].append(root_hist.GetYaxis().GetBinUpEdge(y_bin))
                bins_z["UpperEdges"].append(root_hist.GetZaxis().GetBinUpEdge(z_bin))
                value = root_hist.GetBinContent(bin)
                bin_values.append(value)
    
    # Store the data in a dictionary for pandas
    data = {}
    bin_dims = [bins_x,bins_y,bins_z]
    for d in range(len(bin_dims)):
        data["BinCenters:{}".format(coords[d].name)] = bin_dims[d]["Centers"]
        data["BinLow:{}".format(coords[d].name)] = bin_dims[d]["LowerEdges"]
        data["BinUp:{}".format(coords[d].name)] = bin_dims[d]["UpperEdges"]
    data["Cross sections"] = bin_values
    
    return data

# ------------------------------------------------------------------------------

def get_data(root_hist, coords):
    """ Extract the bin centers and cross section values from the given
        histogram.
    """
    dim = root_hist.GetDimension()
    data = 0

    # Exact extraction depends on dimensionality
    if (dim == 1):
        data = get_data_1d(root_hist, coords)
    elif (dim == 2):
        data = get_data_2d(root_hist, coords)
    elif (dim == 3):
        data = get_data_3d(root_hist, coords)
      
    return data

# ------------------------------------------------------------------------------

def get_distr_filebase(distr_name, energy, eM_chirality, eP_chirality):
    """ Filename convention for the distributions. 
    """
    eM_ID = ""
    eP_ID = ""
    
    if (eM_chirality == -1):
        eM_ID = "eL"
    elif (eM_chirality == 1):
        eM_ID = "eR"
    else:
        raise ValueError("Unknown e- chirality: {}".format(eM_chirality))
        
    if (eP_chirality == -1):
        eP_ID = "pL"
    elif (eP_chirality == 1):
        eP_ID = "pR"
    else:
        raise ValueError("Unknown e+ chirality: {}".format(eP_chirality))
      
    return "{}_{}_{}{}".format(distr_name,energy,eM_ID,eP_ID)

# ------------------------------------------------------------------------------

def get_hist_ptr_1d(rdf, distr_name, coords):
    """ Get TH1D histogram pointer. """
    th1_setup = ROOT.TH1D(distr_name, distr_name,
                          coords[0].n_bins, coords[0].min, coords[0].max)
    return rdf.Histo1D(ROOT.RDF.TH1DModel(th1_setup), coords[0].name)
    
def get_hist_ptr_2d(rdf, distr_name, coords):
    """ Get TH2D histogram pointer. """
    th2_setup = ROOT.TH2D(distr_name, distr_name,
                          coords[0].n_bins, coords[0].min, coords[0].max,
                          coords[1].n_bins, coords[1].min, coords[1].max)
    return rdf.Histo2D(ROOT.RDF.TH2DModel(th2_setup),
                       coords[0].name, coords[1].name)
  
def get_hist_ptr_3d(rdf, distr_name, coords):
    """ Get TH3D histogram pointer. """
    th3_setup = ROOT.TH3D(distr_name, distr_name,
                          coords[0].n_bins, coords[0].min, coords[0].max,
                          coords[1].n_bins, coords[1].min, coords[1].max,
                          coords[2].n_bins, coords[2].min, coords[2].max)
    return rdf.Histo3D(ROOT.RDF.TH3DModel(th3_setup),
                       coords[0].name, coords[1].name, coords[2].name)

def get_hist_ptr(rdf, distr_name, coords):
    """ Get a histogram pointer from the RDataFrame according to the coordinates 
        given.
    """
    hist_ptr = None 
    dim = len(coords)
    if (dim == 1):
      hist_ptr = get_hist_ptr_1d(rdf, distr_name, coords)
    elif (dim == 2):
      hist_ptr = get_hist_ptr_2d(rdf, distr_name, coords)
    elif (dim == 3):
      hist_ptr = get_hist_ptr_3d(rdf, distr_name, coords)
    else:
        raise ValueError("Invalid hist dimension: {}".format(dim))
    return hist_ptr

# ------------------------------------------------------------------------------

def get_bin_range_1d(hist):
    """ Return correct index range for 1D histogram. """
    bin_range = []
    for x_bin in range(0, hist.GetNbinsX()+2):
          bin = hist.GetBin(x_bin)
              
          # Skip overflow and underflow bins
          if hist.IsBinUnderflow(bin) or hist.IsBinOverflow(bin): 
              continue
          
          bin_range.append(bin)
    return bin_range
          
    
def get_bin_range_2d(hist):
    """ Return correct index range for 2D histogram. """
    bin_range = []
    for x_bin in range(0, hist.GetNbinsX()+2):
        for y_bin in range(0, hist.GetNbinsY()+2):
            bin = hist.GetBin(x_bin, y_bin)
            
            # Skip overflow and underflow bins
            if hist.IsBinUnderflow(bin) or hist.IsBinOverflow(bin): 
                continue

            bin_range.append(bin)
    return bin_range


def get_bin_range_3d(hist):
    """ Return correct index range for 3D histogram. """
    bin_range = []
    for x_bin in range(0, hist.GetNbinsX()+2):
        for y_bin in range(0, hist.GetNbinsY()+2):
            for z_bin in range(0, hist.GetNbinsZ()+2):
                bin = hist.GetBin(x_bin, y_bin, z_bin)
                
                # Skip overflow and underflow bins
                if hist.IsBinUnderflow(bin) or hist.IsBinOverflow(bin): 
                    continue

                bin_range.append(bin)
    return bin_range

def get_bin_range(hist):
    """ Return the bin index range that corresponds to the way the bin 
        coordinates where extracted from the histogram.
    """
    bin_range = []
    dim = hist.GetDimension()
    if (dim == 1):
        bin_range = get_bin_range_1d(hist)
    elif (dim == 2):
        bin_range = get_bin_range_2d(hist)
    elif (dim == 3):
        bin_range = get_bin_range_3d(hist)
    else:
        raise ValueError("Invalid hist dimension: {}".format(dim))
    return bin_range

# ------------------------------------------------------------------------------