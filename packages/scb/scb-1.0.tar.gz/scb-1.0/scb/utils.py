__author__ = "Simon Pantzare"
__copyright__ = "Copyright 2012, Simon Pantzare"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "simon@pewpewlabs.com"
__status__ = "Production"

import os


def data_file_path(filename):
    project_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(project_dir, 'data')
    return os.path.join(data_dir, filename)
