r"""
Python components for modelling list colourings of graphs.

This module provides several different models of list-colouring problems. 
Constraint models using the ``python-constraint`` and ``or-tools`` libraries
are the first to be implemented.

AUTHORS:

- Matthew Henderson (2010-12-23): initial version
"""

#********************************************************************************
#       Copyright (C) 2010 Matthew Henderson <matthew.james.henderson@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#********************************************************************************

from vizing.models.pythonconstraint import _CP_model_
#from vizing.models.ortools import _or_CP_model_

def list_colouring(graph, list_assignment, model = 'CP'):

    r"""
    This function returns a list-colouring of a list-colourable graph.

    INPUT:

    - ``graph`` -- A ``networkx`` graph.
    - ``list_assignment`` -- A mapping from nodes of ``graph`` to lists of colours.
    - ``model`` -- Choices are 'CP' for constraint programming via 
      ``python-constraint`` or ``or`` for constraint programming via Google 
      ``or-tools``.

    OUTPUT:

    ``dictionary`` -- the list colouring

    EXAMPLES:

    >>> import networkx
    >>> G = networkx.complete_graph(10)
    >>> L = dict([(node, range(10)) for node in G.nodes()])
    >>> from vizing.models import list_colouring
    >>> list_colouring(G, L, model = 'CP')
    {0: [9], 1: [8], 2: [7], 3: [6], 4: [5], 5: [4], 6: [3], 7: [2], 8: [1], 9: [0]}

    AUTHORS:
    - Matthew Henderson (2010-12-23)
    """

    if model == 'CP':
        return _CP_model_(graph, list_assignment).first_solution()
    if model == 'or':
        return _or_CP_model_(graph, list_assignment).first_solution()
    else:
        raise Exception('No such model')


