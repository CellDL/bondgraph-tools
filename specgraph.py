from celldltools.graph2celldl import Graph2CellDL

from bondgraph.bondgraph import load_model
from bondgraph.bondgraph.cellml import CellMLModel
from bondgraph.bondgraph.template import TemplateRegistry


template = './data/vascular-segment-template.ttl'
registry = TemplateRegistry(template)

specification = 'data/single-segment.ttl'
output = 'single-segment'

#specification = './data/stomach-spleen.ttl'
#output = 'stomach-spleen'


model = load_model(specification, registry)
if model is not None:
    if model.disconnected:
        raise ValueError('Model is not a connected bondgraph...')

    G = model.nx_graph()
    celldl = Graph2CellDL(G)
    celldl.save_diagram(f'{output}.svg')

    cellml = CellMLModel(model.name)
    for node in model.nodes:
        cellml.add_node(node)
    with open(f'{output}.cellml', 'wb') as fp:
        fp.write(cellml.to_xml())
