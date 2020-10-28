import ROOT
from pathlib import Path

# ------------------------------------------------------------------------------

""" Output helper classes and functions.
"""

# ------------------------------------------------------------------------------

def create_dir(dir):
  """ Try to create the given directory and it's parents.
  """
  Path(dir).mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------------------

class OutputInfo:
  """ Class containing typical output information.
  """
  def __init__(self,output_dir,distr_name,create_plots=True):
    self.dir = output_dir
    self.distr_name = distr_name
    self.create_plots = create_plots
    
    # Create the needed output directory structure
    create_dir(output_dir)
        
# ------------------------------------------------------------------------------