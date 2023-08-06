#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

from image_widget import ImageWidget
from dateedit import DateEdit, DateTimeEdit
from greedy_treeview import GreedyTreeView
from fk_entry import FkEdit
from interval_entry import IntervalEdit

from misc import add_stock_icons

SK_ICONS = (
    ('cal15.png', 'sk-calendar'),
    ('keys.png', 'sk-pkeys'),
    ('table-load.png', 'sk-table-load'),
    )

add_stock_icons(*SK_ICONS)

#path = os.path.split(os.path.dirname(__file__))[0]

