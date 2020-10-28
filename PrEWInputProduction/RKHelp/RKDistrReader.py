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
            
            distr.xsections_LR = np.array([float(xsection) for xsection in entry.differential_sigma_LR])
            distr.xsections_RL = np.array([float(xsection) for xsection in entry.differential_sigma_RL])
            distr.xsections_LL = np.array([float(xsection) for xsection in entry.differential_sigma_LL])
            distr.xsections_RR = np.array([float(xsection) for xsection in entry.differential_sigma_RR])
            
            distr.coef_labels = [label for label in str(entry.differential_PNPC_label).split(";") if not label == ""]
            distr.coefs_LR = np.array([ [float(entry.differential_PNPC_LR[row][col]) for col in range(entry.differential_PNPC_LR.GetNcols())] for row in range(n_rows)])
            distr.coefs_RL = np.array([ [float(entry.differential_PNPC_RL[row][col]) for col in range(entry.differential_PNPC_RL.GetNcols())] for row in range(n_rows)])
            distr.coefs_LL = np.array([ [float(entry.differential_PNPC_LL[row][col]) for col in range(entry.differential_PNPC_LL.GetNcols())] for row in range(n_rows)])
            distr.coefs_RR = np.array([ [float(entry.differential_PNPC_RR[row][col]) for col in range(entry.differential_PNPC_RR.GetNcols())] for row in range(n_rows)])
            self.distrs.append(distr)
            
    def get_distr(self, name):
        """ Return the distribution of the given name.
        """
        found_distrs = []
        for distr in self.distrs:
            if (distr.name == name):
                found_distrs.append(distr)
                
        n_found = len(found_distrs)
        if (n_found == 0):
            raise ValueError("Didn't find distribution {}".format(name))
        elif (n_found > 1):
            raise ValueError("Found more than one distribution {}, found {}".format(name, n_found))
          
        return found_distrs[0]

# ------------------------------------------------------------------------------

def test():
    """ Test the RKDistr and RKDistrReader classes.
    """
    reader = RKDistrReader(
        "/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/WW_charge_separated/distributions/combined/Distribution_250GeV_WW_semilep_AntiMuNu.root",
        "MinimizationProcesses250GeV"
    )
    
    for distr in reader.distrs:
        print(distr.name)
        if (len(distr.bin_centers[0]) == 3):
            print([distr.bin_centers[:,0][10*10*i] for i in range(20)])
            print([distr.bin_centers[:,1][10*i] for i in range(12)])
            print(distr.bin_centers[:,2][:12])
            
            for i in range(len(distr.coefs_LR[0])):
                for b in range(int(len(distr.coefs_LR)/10)):
                    coefs = distr.coefs_LR[10*b:10*b+10,i]
                    mean = np.mean(coefs)
                    std = np.std(coefs)
                    if ( std > 0.001*abs(mean) ):
                        print("Bin{}: Coef{}: Mean = {}, Std = {}".format(b,i,mean,std))

# ------------------------------------------------------------------------------

# If this script is called directly (not imported), run the test
if __name__ == "__main__":
    test()

# ------------------------------------------------------------------------------