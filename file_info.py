import math
import os

FILE_PART_SIZE = 1024 * 1000

class FileInfo:

    def __init__(self, size_of_file, files_path, file_name, type):
        self.type = type  # SENT/RECEIVED
        self.file_name = file_name
        self.size_of_file = size_of_file
        self.file_path = os.path.join(files_path, file_name)
        self.is_ready = False
        self.parts = []
        self.max_num_of_parts = math.ceil(size_of_file/FILE_PART_SIZE)
        self.percentage = 0
        self.file = open(self.file_path, 'ab')

    def add_part(self, part=None):
        if self.is_ready:
            return

        self.parts.append(part)
        self.percentage = len(self.parts) / self.max_num_of_parts * 100

        if self.type == "RECEIVED":
            self.file.write(part.content)
            if self.percentage == 100.0:
                self.file.close()
                self.parts = []
                self.is_ready = True

    def merge_file(self):
        self.parts.sort(key=lambda x: x.frame_number)
        file = b''
        for part in self.parts:
            file += part.content
        self.parts = []
        with open(self.file_path, 'wb') as f:
            f.write(file)
        self.is_ready = True
