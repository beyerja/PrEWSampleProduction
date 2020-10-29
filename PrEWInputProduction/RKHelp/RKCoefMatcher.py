from copy import copy
import logging as log
import numpy as np
from tqdm import tqdm

import RKDistrReader as RKDR

# ------------------------------------------------------------------------------

class RKCoefMatcher:
    """ Class that helps match the TGC coefficients from Robert Karls 
        matrix element level distributions to new distributions (from MC).
    """
    
    MC_to_RK_names = {
        "WW_muminus" : "WW_semilep_MuAntiNu",
        "WW_muplus" : "WW_semilep_AntiMuNu"
    }
    
    RK_binning = {
        "WW_semilep_MuAntiNu" : ["costh_Wminus_star","costh_l_star","phi_l_star"],
        "WW_semilep_AntiMuNu" : ["costh_Wminus_star","costh_l_star","phi_l_star"]
    }
    
    # Sometimes binning is different (without affecting the cross section)
    RK_bin_manipulator = {
      # Roberts WW distribution have a wrong Phi_l^* binning
      "WW_semilep_MuAntiNu" : lambda x: np.array([x[0], -x[1], (x[2] - np.pi) * 9.0/10.0]),
      "WW_semilep_AntiMuNu" : lambda x: np.array([x[0], -x[1], (x[2] - np.pi) * 9.0/10.0])
    }
    
    def __init__(self, RK_distrs=None):
        self.RK_distrs = [] if (RK_distrs == None) else RK_distrs
        
    def add_RK_file(self, file_path, tree_name):
        """ Use the RK distributions from the tree in the given file.
        """
        for distr in RKDR.RKDistrReader(file_path, tree_name).distrs:
            self.RK_distrs.append(distr)

    def get_distr(self, name):
        """ Return the distribution of the given name.
        """
        found_distrs = []
        for distr in self.RK_distrs:
            if (distr.name == name):
                found_distrs.append(distr)
                
        n_found = len(found_distrs)
        if (n_found == 0):
            raise ValueError("Didn't find distribution {}".format(name))
        elif (n_found > 1):
            raise ValueError("Found more than one distribution {}, found {}".format(name, n_found))
          
        return found_distrs[0]    

    def add_coefs_to_data(self, distr_name, eM_chirality, eP_chirality, distr_data):
        """ Add the correct coefficients to the given distribution.
            Needs the distribution data which contains the bins.
        """
        if not distr_name in self.MC_to_RK_names:
          log.debug("\tNo coefficients found for {}".format(distr_name))
          return distr_data
        else:
          log.debug("Distribution available, will attemp matching.")
        
        RK_name = self.MC_to_RK_names[distr_name]
        RK_distr = self.get_distr(RK_name)
        RK_coords = copy(RK_distr.bin_centers) # Copy RK bin center array
          
        # See if bins are supposed to be manipulated
        bin_manipulator = False
        if RK_name in self.RK_bin_manipulator:
          log.debug("Got bin manipulator.")
          bin_manipulator = self.RK_bin_manipulator[RK_name]
          RK_coords = np.apply_along_axis(bin_manipulator, axis=1, arr=RK_coords)
        
        # Dictionary for collecting the coefficients in the right order
        coef_dict = {}
        for coef_label in RK_distr.coef_labels:
            coef_dict[coef_label] = []
        
        # Find the coefficients for each bin
        bin_range = range(len(distr_data["Cross sections"]))
        for b in tqdm(bin_range, desc="\tMatching RK coefs"):
            # Get the (adjusted coordinates) of
            coords = [distr_data["BinCenters:{}".format(coord_name)][b] for coord_name in self.RK_binning[RK_name]]
            
            # Find the correct bin
            index = None
            diff = np.absolute( RK_coords - coords )
            diff_check = np.all(diff < 0.001, axis=1) # Check which coordinates match up
            indices = np.where(diff_check)[0]
            
            # Check if exactly one index was found
            if len(indices) == 0:
              raise ValueError("Didn't find matching bin {} \nAvailable bins : {}".format(coords,RK_coords))
            elif (len(indices) > 1):
              raise ValueError("Found more than one fitting bin for {}: {}".format(coords,[RK_coords[i] for i in indices]))
            else:
              log.debug("Found index for bin {}.".format(b))
              
            index = indices[0]
            
            # Find and add the appropriate coefs from the RK distribution
            for co in range(len(RK_distr.coef_labels)):
                coef = None
                if (eM_chirality == -1) and (eP_chirality == +1):
                    coef = RK_distr.coefs_LR[index][co]
                elif (eM_chirality == +1) and (eP_chirality == -1):
                    coef = RK_distr.coefs_RL[index][co]
                elif (eM_chirality == -1) and (eP_chirality == -1):
                    coef = RK_distr.coefs_LL[index][co]
                elif (eM_chirality == +1) and (eP_chirality == +1):
                    coef = RK_distr.coefs_RR[index][co]
                else:
                    raise ValueError("Unknown chiralities {} {}".format(eM_chirality, eP_chirality))
                    
                coef_dict[RK_distr.coef_labels[co]].append(coef)
            
        # Add the coefficients to the distribution data
        for coef_name, coefs in coef_dict.items():
            distr_data["Coef:{}".format(coef_name)] = coefs
            
        return distr_data
        
# ------------------------------------------------------------------------------

def default_coef_matcher():
    """ Get the default coef matcher that looks in all known RK distributions (at 250 GeV!!!).
    """
    matcher = RKCoefMatcher()
    matcher.add_RK_file("/afs/desy.de/group/flc/pool/beyerjac/TGCAnalysis/GlobalFit/UnifiedApproach/MinimizationProcessFiles/ROOTfiles/MinimizationProcessesListFile_500_250Full_Elektroweak_menu_2018_04_03.root", "MinimizationProcesses250GeV")
    matcher.add_RK_file("/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/WW_charge_separated/distributions/combined/Distribution_250GeV_WW_semilep_AntiMuNu.root", "MinimizationProcesses250GeV")
    matcher.add_RK_file("/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/WW_charge_separated/distributions/combined/Distribution_250GeV_WW_semilep_MuAntiNu.root", "MinimizationProcesses250GeV")
    return matcher

# ------------------------------------------------------------------------------