r"""
Some useful miscellaneous components.

AUTHORS:

- Matthew Henderson (2010-12-30): initial version
"""

#********************************************************************************
#       Copyright (C) 2010 Matthew Henderson <matthew.james.henderson@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#********************************************************************************
import itertools
from networkx import graph_clique_number, complement

from test_functions import has_colour

def grange(vtc_colouring):
    """The colours used by a colouring (vertex-to-color map)."""
    return list(set((vtc_colouring.values())))

def inverse(vtc_colouring, colour):
    """The vertices where a colour appears in a vertex-to-colour map."""
    return [v for v in vtc_colouring if vtc_colouring[v] == colour]

def vtc_to_ctv(vtc):
    """Translate a verticex-to-colour map into a colour-to-vertices map."""
    return dict([(colour, inverse(vtc, colour)) for colour in grange(vtc)])

def support(list_assignment, nodes, colour):
    """
    A list of those vertices in 'nodes' which have 'colour' in the list 
    associated with that vertex by 'list_assignment'.
    """
    return filter(lambda vertex: has_colour(list_assignment, vertex, colour), nodes)

def support_subgraph(graph, list_assignment, colour):
    """
    The subgraph induced by those vertices of 'graph' which have 'colour' 
    in the list associated by 'list_assignment'.
    """
    return graph.subgraph(support(list_assignment, graph.nodes(), colour))

def independence_number(graph):
    """
    Compute the independence number of 'graph'.
    """
    if graph.number_of_nodes() == 0:
        return 0
    else:
        return graph_clique_number(complement(graph))

def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

