from graph2celldl import Graph2CellDL

#from bondgraph.model import load_model
#from bondgraph.template import BondgraphTemplate

from bondgraph.spec2networkx import bg_spec_to_networkx
#from bondgraph.template import BondgraphTemplate


#template = '/Users/dbro078/CellDL/Bondgraphs/ApiNATOMY/templates/vascular-segment-template.ttl'
#tpl = BondgraphTemplate(template)

#print()

specification = '/Users/dbro078/CellDL/Bondgraphs/ApiNATOMY/models/stomach-spleen.ttl'
#model = load_model(specification)


G = bg_spec_to_networkx(specification)
## #print(G.nodes(data=True))
## print(G.edges())
## celldl = Graph2CellDL(G)
## celldl.save_diagram('stomach.svg')
