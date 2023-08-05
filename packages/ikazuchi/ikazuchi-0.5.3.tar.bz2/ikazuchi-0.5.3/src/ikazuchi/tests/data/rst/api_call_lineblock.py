# -*- coding: utf-8 -*-

from parse_lineblock import DATA_SET as data_set
from utils import add_linebreak

DATA_SET = [(data[1][0][1], add_linebreak(data[1][0][1])) for data in data_set]
