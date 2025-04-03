#===============================================================================

import csv
from pathlib import Path
from pprint import pprint

import networkx as nx

#===============================================================================

from graph2celldl import Graph2CellDL

#===============================================================================

def graph2celldl(G: nx.DiGraph, celldl_file: str, layout_method='bfs'):
#======================================================================
    celldl = Graph2CellDL(G, layout_method=layout_method)
    celldl.save_diagram(Path(celldl_file))


#===============================================================================

def autogen(csv_file: str, celldl_file: str):
    G = nx.DiGraph()
    with open(csv_file) as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            node = row['name']
            G.add_node(node, label=node)
            inputs = row['inp_vessels'].split()
            outputs = row['out_vessels'].split()
            for input in inputs:
                G.add_edge(input, node)
            for output in outputs:
                G.add_edge(node, output)
    graph2celldl(G, celldl_file, layout_method='bfs')

#===============================================================================

def test(debug=False):
    if debug:
        G = nx.DiGraph()
        G.add_edge(0, 1)
        G.nodes[0]['label'] = 'Node 0'
        G.nodes[1]['label'] = 'Node 1'
        nld = nx.node_link_data(G)
        pprint(nld)
    else:
        G = nx.binomial_tree(4)
    graph2celldl(G, 'test.svg')

#===============================================================================

if __name__ == '__main__':
    test()
    autogen('./graph2celldl/data/lung_ROM_vessel.csv', 'lung_ROM.svg')
    autogen('./graph2celldl/data/control_phys_vessel.csv', 'control_phys.svg')

#===============================================================================
