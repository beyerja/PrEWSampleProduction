# ------------------------------------------------------------------------------

class SystematicsOptions:
  """ Class that stores the settings for how which systematic effects should be 
      considered.
  """
  
  def __init__(self, use_muon_acc=False, costh_branch="costh"):
    """ All the potential options can be set here and are turned off by default.
    """
    self.use_muon_acc = use_muon_acc
    self.costh_branch = costh_branch # Can be str or array of str
    
# ------------------------------------------------------------------------------