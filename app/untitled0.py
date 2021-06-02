# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 12:50:39 2021

@author: simon
"""

from rtreelib import RTree, Rect
from rtreelib.diagram import create_rtree_diagram


# Create an RTree instance with some sample data
t = RTree(max_entries=4)
t.insert('a', Rect(0, 0, 3, 3))
t.insert('b', Rect(2, 2, 4, 4))
t.insert('c', Rect(1, 1, 2, 4))
t.insert('d', Rect(8, 8, 10, 10))
t.insert('e', Rect(7, 7, 9, 9))

# Create a diagram of the R-tree structure
create_rtree_diagram(t)