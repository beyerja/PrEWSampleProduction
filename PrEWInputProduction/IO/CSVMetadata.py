class CSVMetadata:
    """ Class to add metadata to the top of a CSV file.
    """
    begin_marker = "#BEGIN-METADATA"
    end_marker = "#END-METADATA"
    coef_marker = "Coef"

    def __init__(self):
        self.metadata = {}

    def __setitem__(self, index, value):
        self.metadata[index] = value

    def __getitem__(self, index):
        return self.metadata[index]
            
    def add_coef(self, base_name, coef_name, value):
        """ Add a global coefficient as metadata.
            Requires the base_name (describing the thing the coef is about),
            the specific coef_name and its value.
        """
        full_name = "{}|{}_{}".format(self.coef_marker,base_name,coef_name)
        self.metadata[full_name] = value

    def get_metadata_str(self):
        """ Get the current metadata string.
        """
        metadata_str = self.begin_marker + "\n"
        for name, value in self.metadata.items():
            metadata_str += "{}: {}\n".format(name, value)
        metadata_str += self.end_marker + "\n"
        return metadata_str

    def write(self, csv_path):
        """ Write all the given metadata to the top of the file.
        """
        metadata_str = self.get_metadata_str()

        file = open(csv_path, 'r+')
        data = file.read() # read previous file contents 
        file.seek(0,0)  # get to the first position
        file.write("{}{}".format(metadata_str,data))
        file.close()
