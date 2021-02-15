# ------------------------------------------------------------------------------

""" Naming conventions within this framework.
"""

# ------------------------------------------------------------------------------
# File naming conventions

def csv_file_name(distr_name, energy, eM_chirality, eP_chirality):
    """ CSV filename convention for the distributions. 
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