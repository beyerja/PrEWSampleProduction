# External modules
import argparse
import re # Regular expression searches

def find_filenumber(file_path):
  num_regex = re.search('[0-9]*\.slcio$',file_path)
  if num_regex:
    return int(num_regex.group(0).replace(".slcio",""))
  raise Exception("No file number found in file {}".format(file_path))
    
def find_ID(file_path):
  ID_regex = re.search('I(.*?)\.',file_path)
  if ID_regex:
    return int(ID_regex.group(0).replace("I","").replace(".",""))
  raise Exception("No ID found in file {}".format(file_path))
    
def find_chirality(file_path):
  chi_regex = re.search('e[L|R]\.p[L|R]',file_path)
  if chi_regex:
    chi = chi_regex.group(0)
    e_chi_str = -1.000 if "eL" in chi else 1.000
    p_chi_str = -1.000 if "pL" in chi else 1.000
    return "@({}),@({})".format(e_chi_str,p_chi_str)
  raise Exception("No chirality found in file {}".format(file_path))
    
def main():
  description = """
    Interpret the given LCIO filename, finding information that is encoded in it.
  """
  parser = argparse.ArgumentParser(description=description)
  parser.add_argument("--file", type=str, required=True, help="The LCIO file path")
  parser.add_argument("--file-number", action='store_true', help="Find the file number (out of all the files for that process)")
  parser.add_argument("--process-ID", action='store_true', help="Find the process ID in the given filename")
  parser.add_argument("--chirality", action='store_true', help="Find the chirality in the filename and return it sindarin-style")
  args = parser.parse_args()
  
  if args.file_number:
    print(find_filenumber(args.file))
  elif args.process_ID:
    print(find_ID(args.file))
  elif args.chirality:
    print(find_chirality(args.file))


if __name__ == "__main__":
  main()