import csv
import os
from flask import current_app

class CSVdata:
    def __init__(self, filename):
        self.file = os.path.join(current_app.config['PROJECT_ROOT'], filename)
        print(current_app.config['PROJECT_ROOT'])


    def as_dict(self,prop):
        read = csv.DictReader(open(self.file, 'r'))
        as_dict = []

        for line in read:
            if line[prop] == 'x':
                as_dict.append(line)

        return as_dict
