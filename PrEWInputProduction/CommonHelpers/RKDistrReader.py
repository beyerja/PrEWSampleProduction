import ROOT
import cppyy
import numpy as np

# ------------------------------------------------------------------------------

""" Classes needed to read the distribution files provided by Robert Karl.
"""

# ------------------------------------------------------------------------------

class RKDistr:
    """ Class describing a distribution created by Robert Karl.
    """

    def __init__(self):
        self.name = ""
        self.bin_centers = []
        
        self.xsections_LR = []
        self.xsections_RL = []
        self.xsections_LL = []
        self.xsections_RR = []
        
        self.coef_labels = []
        self.coefs_LR = []
        self.coefs_RL = []
        self.coefs_LL = []
        self.coefs_RR = []

# ------------------------------------------------------------------------------

class RKDistrReader:
    """ Class that can read the distributions (cross sections, bins, 
        coefficients, ...) that are stores in files created by Robert Karl.
    """
    
    def __init__(self, file_path, tree_name):
        self.distrs = []
        
        # Read the distributions form the file
        file = ROOT.TFile(file_path)
        tree = file.Get(tree_name)
        self.read_distrs(tree)
        file.Close()
        
    def read_distrs(self, tree):
        """ Read all the distributions from the given file
        """
        tree.GetEntry(0)
        for entry in tree:         
            # Each entry is a distribution
            distr = RKDistr()
            
            # Extract all the distribution quantities from the tree
            distr.name = str(entry.describtion)
            
            n_rows = entry.angular_center.GetNrows()
            n_cols = entry.angular_center.GetNcols()
            if (distr.name in ["Zhadronic", "Zleptonic"]):
              n_cols = 1 # This is stores falsly in the TTree
            
            distr.bin_centers = np.array([[float(entry.angular_center[row][col]) for col in range(n_cols)] for row in range(n_rows)])
            
            distr.xsections_LR = [float(xsection) for xsection in entry.differential_sigma_LR]
            distr.xsections_RL = [float(xsection) for xsection in entry.differential_sigma_RL]
            distr.xsections_LL = [float(xsection) for xsection in entry.differential_sigma_LL]
            distr.xsections_RR = [float(xsection) for xsection in entry.differential_sigma_RR]
            
            distr.coef_labels = [str(label) for label in entry.differential_PNPC_label]
            distr.coefs_LR = entry.differential_PNPC_LR
            distr.coefs_RL = entry.differential_PNPC_RL
            distr.coefs_LL = entry.differential_PNPC_LL
            distr.coefs_RR = entry.differential_PNPC_RR
            self.distrs.append(distr)

# ------------------------------------------------------------------------------

def test():
    """ Test the RKDistr and RKDistrReader classes.
    """
    reader = RKDistrReader(
        "/home/jakob/Documents/DESY/MountPoints/POOLMount/TGCAnalysis/GlobalFit/UnifiedApproach/MinimizationProcessFiles/ROOTfiles/MinimizationProcessesListFile_500_250Full_Elektroweak_menu_2018_04_03.root",
        "MinimizationProcesses250GeV"
    )

# ------------------------------------------------------------------------------

# If this script is called directly (not imported), run the test
if __name__ == "__main__":
    test()

# ------------------------------------------------------------------------------
