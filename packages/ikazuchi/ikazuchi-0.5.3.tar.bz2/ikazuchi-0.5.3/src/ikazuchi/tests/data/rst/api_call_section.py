# -*- coding: utf-8 -*-

from parse_section import DATA_SET as data_set
from utils import del_linebreak

DATA_SET = [(del_linebreak(data[1][0][1]), data[1][0][1]) for data in data_set]
