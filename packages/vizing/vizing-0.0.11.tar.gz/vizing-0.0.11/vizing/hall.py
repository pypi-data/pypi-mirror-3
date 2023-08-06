r"""
Python components for calculating Hall inequalities.

AUTHORS:

- Matthew Henderson (2010-12-30): initial version
"""

#********************************************************************************
#       Copyright (C) 2010 Matthew Henderson <matthew.james.henderson@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#********************************************************************************

from vizing.utils import support_subgraph, independence_number, powerset

def hall_subgraph(graph, list_assignment, colour):
    """

    """
    return support_subgraph(graph, list_assignment, colour)

def hall_number(graph, list_assignment, colour):
    """
    Compute the independence number of the subgraph induced by those 
    vertices in 'graph' having 'colour' in their list. Not to be confused with
    Hall number in the literature. 
    """
    return independence_number(hall_subgraph(graph, list_assignment, colour))

def hall_numbers(graph, list_assignment, colours):
    """
    A list of Hall numbers for each monochromatic subgraph.
    """
    return [hall_number(graph, list_assignment, colour) for colour in colours]

def hall_sum(graph, list_assignment, colours):
    """
    Sum Hall numbers over all monochromatic subgraphs.
    """
    return sum(hall_numbers(graph, list_assignment, colours))

def hall_inequality(graph, list_assignment, colours):
    """
    Decide whether the Hall inequality for graph is satisfied
    """
    return hall_sum(graph, list_assignment, colours) >= len(graph.nodes())

def hall_inequality_induced_by(graph, list_assignment, colours, vertices):
    """
    Check Hall's inequality for a subgraph of 'graph' induced by 'vertices'.
    """
    return hall_inequality(graph.subgraph(vertices), list_assignment, colours)

def halls_condition_restricted_to(graph, list_assignment, colours, node_subsets):
    """
    Check Hall's condition restricted to subgraphs induced by node_subsets.
    """
    return all(map(lambda x: hall_inequality_induced_by(graph, list_assignment, colours, x), node_subsets))

def halls_condition(graph, list_assignment, colours):
    """
    Check Hall's condition.
    """
    return halls_condition_restricted_to(graph, list_assignment, colours, powerset(graph.nodes()))
