import ROOT

# ------------------------------------------------------------------------------

""" Output helper classes and functions.
"""

# ------------------------------------------------------------------------------

class OutputInfo:
    """ Class containing typical output information.
    """
    def __init__(self,output_dir,distr_name,create_plots=True):
        self.dir = output_dir
        self.distr_name = distr_name
        self.create_plots = create_plots

# ------------------------------------------------------------------------------