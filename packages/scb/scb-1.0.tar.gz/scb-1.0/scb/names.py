__author__ = "Simon Pantzare"
__copyright__ = "Copyright 2012, Simon Pantzare"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "simon@pewpewlabs.com"
__status__ = "Production"

import functools

import xlrd

import utils

MALE = 1
FEMALE = 2
GENDERS = [MALE, FEMALE]
WORKBOOK_FILENAMES = {
    MALE: 'be0001namntab12.xls', 
    FEMALE: 'be0001namntab11.xls'}


def names(gender):
    file_path = utils.data_file_path(WORKBOOK_FILENAMES[gender])
    book = xlrd.open_workbook(file_path)
    sheet = book.sheets()[0]
    name_col = sheet.col(0)
    header_cols = 4
    names = [n.value.strip() for n in name_col[header_cols:]]
    return names


male = functools.partial(names, MALE)
female = functools.partial(names, FEMALE)
