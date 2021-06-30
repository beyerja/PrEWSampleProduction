# External modules
import argparse
import numpy as np

def get_dev_scale(config_path):
  """ Find the scale of the tgc deviations in the config file.
  """
  scale_id="scale="
  with open(config_path, "r") as cf:
    scale_lines = [l for l in cf if l.startswith(scale_id)]
    if (len(scale_lines) != 1):
      raise Exception("Found {} scale lines in config file".format(len(scale_lines)))
    return float(scale_lines[0].strip().replace(scale_id,""))
    
def get_g1z_ka_la_points(dev_points,dev_scale):
  """ Given the deviation points and their scale, return the values of the 
      3 free cTGCs g1z, kappa_gamma and lambda_gamma.
  """
  # Important: order of points is: g1Z, kappa_gamma, lambda_gamma
  return np.array([1.0, 1.0, 0.0]) + dev_points * dev_scale
  
def get_single_cTGC_point_sindarin(g1z_ka_la_point):
  """ Get the sindarin describing one cTGC point completely.
  """
  gauge_conditions = "  kz = 1.0 - (ka - 1.0) * sw**2/cw**2 + (g1z - 1.0)\n  lz = la\n"
  return "  g1z = {}\n  ka = {}\n  la = {}\n".format(
           g1z_ka_la_point[0], g1z_ka_la_point[1], g1z_ka_la_point[2]) + gauge_conditions
  
def get_cTGC_sindarin(g1z_ka_la_points):
  """ Get the sindarin for all cTGC points.
  """
  sindarin_str = "{\n"
  for g1z_ka_la_point in g1z_ka_la_points:
    sindarin_str += get_single_cTGC_point_sindarin(g1z_ka_la_point) + "},{\n"
  sindarin_str = sindarin_str[:-3] # Remove last ",{\n"
  
  return sindarin_str
    
def main():
  description = """
    Given a point file containing the cTGC deviations and a config file containing their scaling, return the Sindarin that accurately describes these points in the SM_ac_CKM model.
  """
  parser = argparse.ArgumentParser(description=description)
  parser.add_argument("--config-path", type=str, required=True, help="File path containing the general TGC configuration")
  parser.add_argument("--points-path", type=str, required=True, help="File path containing the TGC deviation points")
  args = parser.parse_args()
  
  dev_scale = get_dev_scale(args.config_path)
  dev_points = np.loadtxt(args.points_path)
  
  g1z_ka_la_points = get_g1z_ka_la_points(dev_points,dev_scale)
  
  print(get_cTGC_sindarin(g1z_ka_la_points))

if __name__ == "__main__":
  main()