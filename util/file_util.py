

class FileUtil(object):
    @staticmethod
    def read_file(file):
        with open(file, "rt") as f:
            return f.read()

    @staticmethod
    def read_file_list(file):
        with open(file, "rt") as f:
            return f.readlines()

