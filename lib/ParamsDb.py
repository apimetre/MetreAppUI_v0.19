import json

class ParamsDb:
    def __init__(self, path, filename):
        self.path = path
        self.filename = filename
        self.file_path = path + filename
        self.data = {}

    def read_data(self):
        self.data = self.json_file_to_dict(self.file_path)
        return self.data

    def write_data(self):
        self.dict_to_json_file(self.file_path, self.data)

    def dict_to_json_file(self, file_path, db_dict):
        with open(file_path, 'w') as f:
          json.dump(db_dict, f)
        
    def json_file_to_dict(self, file_path):
        with open(file_path) as f:
            return json.load(f)

    def file_to_string(self, file_path):
        with open(file_path) as f:
            return f.read()

    def dict_to_csv(self, file_path, db_dict):
        with open(file_path, 'wt') as f:
            for key, value in db_dict.items():
                f.write("{},".format(key))
            f.write("\r\n")
            for key, value in db_dict.items():
                f.write("{},".format(value))
            f.write("\r\n")

class DotNotation:
    def __init__(self, db_dict):
        self.data = db_dict
        for key, value in self.data.items():
            setattr(self, key, value)
