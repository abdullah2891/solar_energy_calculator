import sys
py_ver = 2
if (sys.version_info > (3, 0)):
    py_ver = 3

import numpy as np

def get_data(files):
    """Parses data from multiple files, and concatenates them"""
    data = []
    for fn in files:
        data += parse_data(fn).tolist()
    return np.array(data)

def parse_data(fn):
    """
    NREL csv data parser
    """
    data = []
    with open(fn, "rb") as f:
        for line in f:
            if py_ver == 3:
                # Python 3 code in this block
                dline = "".join(filter(lambda char: char != '"', line.decode())).split(",")
            else:
                # Python 2 code in this block
                dline = line.translate(None, '"').split(",")
            
            if len(dline) == 11 and dline[0].isdigit():
                data.append([float(i) for i in dline])

    return np.array(data)