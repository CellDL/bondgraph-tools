#===============================================================================
#
#  CellDL and bondgraph tools
#
#  Copyright (c) 2020 - 2025 David Brooks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#===============================================================================

from celldltools.graph2celldl import Graph2CellDL

from bondgraph.bondgraph import load_model, __version__
from bondgraph.bondgraph.cellml import CellMLModel
from bondgraph.bondgraph.template import TemplateRegistry

#===============================================================================

def main():
#==========
    import argparse

    parser = argparse.ArgumentParser(description='Generate CellML for a bondgraph model specified in RDF')
    parser.add_argument('--version', action='version', version=f'Version {__version__}')
    parser.add_argument('--celldl', metavar='CELLDL_FILE', help='The name for the CellDL (SVG) output file. Optional')
    parser.add_argument('template', metavar='TEMPLATE_FILE', help='A template file defining bondgraph components in RDF')
    parser.add_argument('model', metavar='MODEL_FILE', help='The RDF definition of a model')
    parser.add_argument('cellml', metavar='CELLML_FILE', help='The name for the resulting CellML file')
    args = parser.parse_args()

    registry = TemplateRegistry(args.template)
    model = load_model(args.model, registry)
    if model is None:
        raise TypeError('The model could not be loaded')
    elif model.disconnected:
        raise ValueError('Model is not a connected bondgraph...')

    if args.celldl:
        G = model.nx_graph()
        celldl = Graph2CellDL(G)
        celldl.save_diagram(args.celldl)

    cellml = CellMLModel(model.name)
    for node in model.nodes:
        cellml.add_node(node)
    with open(args.cellml, 'wb') as fp:
        fp.write(cellml.to_xml())

#===============================================================================

if __name__ == '__main__':
#=========================
    main()

#===============================================================================
