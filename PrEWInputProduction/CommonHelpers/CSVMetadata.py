class CSVMetadata:
    """ Class to add metadata to the top of a CSV file.
    """
    begin_marker = "#BEGIN-METADATA"
    end_marker = "#END-METADATA"

    marker_map = {
        "name": "Name",
        "energy": "Energy",
        "e- chirality": "e-Chirality",
        "e+ chirality": "e+Chirality"
    }

    def __init__(self):
        self.metadata = {}

    def add(self, name, value):
        """ Add the given attribute metadata.
        """
        if not name in self.marker_map.keys():
            raise ValueError(
                "Unknown attribute {}, only know {}.", name, self.marker_map.keys())
        else:
            self.metadata[name] = value

    def get_metadata_str(self):
        """ Get the current metadata string.
        """
        metadata_str = self.begin_marker + "\n"
        for name, value in self.metadata.items():
            metadata_str += "{}: {}\n".format(self.marker_map[name], value)
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
