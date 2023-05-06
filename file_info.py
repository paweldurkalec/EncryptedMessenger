import math
import os

FILE_PART_SIZE = 1024

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

    def add_part(self, part=None):
        if self.is_ready:
            return

        if self.type == "SENT":
            self.parts.append(None)
            self.percentage = len(self.parts) / self.max_num_of_parts * 100
        if self.type == "RECEIVED":
            self.parts.append(part)
            self.percentage = len(self.parts)/self.max_num_of_parts * 100
            if self.percentage == 100.0:
                self.merge_file()

    def merge_file(self):
        self.parts.sort(key=lambda x: x.frame_number)
        file = b''
        for part in self.parts:
            file += part.content
        self.parts = []
        with open(self.file_path, 'wb') as f:
            f.write(file)
        self.is_ready = True
