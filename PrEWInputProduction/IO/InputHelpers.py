import ROOT

# ------------------------------------------------------------------------------

""" Input helper classes and functions.
"""

# ------------------------------------------------------------------------------

class InputInfo:
    """ Class containing typical input information.
    """
    def __init__(self,file_path,tree_name,energy):
        self.file_path = file_path
        self.tree_name = tree_name
        self.energy = energy

    def get_rdf(self):
        """ Get the ROOT RDataFrame for the given tree in the input file.
        """
        return ROOT.RDataFrame(self.tree_name, self.file_path)
# ------------------------------------------------------------------------------