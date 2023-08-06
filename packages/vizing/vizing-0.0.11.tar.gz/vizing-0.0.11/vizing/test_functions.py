r"""
Python components for testing list colourings of graphs.

- Matthew Henderson (2010-12-23): initial version

EXAMPLES:
"""

#********************************************************************************
#       Copyright (C) 2010 Matthew Henderson <matthew.james.henderson@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#********************************************************************************   

import itertools
from networkx import graph_clique_number

def is_independent(graph, nodes):
    """Decides whether of not the subgraph of 'graph' induced by nodes in 
    'nodes' is an independent set or not."""
    if len(nodes) == 0:
        return True
    else:
        return graph_clique_number(graph.subgraph(nodes)) == 1

def is_exact(graph, colouring):
    """Decides whether exactly every vertex of 'graph' is coloured."""
    coloured_vertices = list(itertools.chain.from_iterable(colouring.values()))
    coloured_vertices.sort()
    return coloured_vertices == graph.nodes()

def is_proper(graph, colouring):
    """Decides whether or not 'colouring' is a proper colouring of the vertices
    of 'graph'."""
    return is_exact(graph, colouring) and all(map(lambda nodes: is_independent(graph, nodes), colouring.values()))

def has_colour(list_assignment, vertex, colour):
    """Decides whether or not 'colour' is a member of the list assigned to 
    'vertex' by the 'list_assignment'."""
    return colour in list_assignment.get(vertex)

def is_list_colouring(graph, list_assignment, colouring):
    """Decides whether or not 'colouring' is a list colouring of 'graph', 
    according to the 'list_assignment' given."""
    return all([has_colour(list_assignment, vertex, colour) for colour in colouring for vertex in colouring.get(colour)])

def is_proper_list_colouring(graph, list_assignment, colouring):
    """Decides whether or not 'colouring' is a proper list colouring of 
    'graph', according to the 'list_assignment' given."""
    return is_proper(graph, colouring) and is_list_colouring(graph, list_assignment, colouring)

