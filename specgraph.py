from graph2celldl import Graph2CellDL

from bondgraph.spec2networkx import bg_spec_to_networkx


G = bg_spec_to_networkx('/Users/dbro078/CellDL/Bondgraphs/ApiNATOMY/models/stomach-spleen.ttl')
celldl = Graph2CellDL(G)
celldl.save_diagram('stomach.svg')
