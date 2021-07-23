# ------------------------------------------------------------------------------

class PhysicsOptions:
  """ Class that stores the settings for how which physics effects should be 
      considered.
  """
  
  def __init__(self, 
               use_TGCs=False, TGC_config_path=None, TGC_points_path=None, 
                                                     TGC_weight_base=None):
    """ All the potential options can be set here and are turned off by default.
    """
    self.use_TGCs = use_TGCs
    self.TGC_config_path = TGC_config_path
    self.TGC_points_path = TGC_points_path
    self.TGC_weight_base = TGC_weight_base
    
# ------------------------------------------------------------------------------