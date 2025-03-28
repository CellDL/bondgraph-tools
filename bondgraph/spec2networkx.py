#===============================================================================

from pathlib import Path

#===============================================================================

import networkx as nx
import rdflib

#===============================================================================

from .queries import MODEL_QUERY, MODEL_PREFIXES, TEMPLATE_PREFIXES
from .namespaces import NamespaceMap

#===============================================================================

# (rdflib.term.URIRef('file:///Users/dbro078/CellDL/Bondgraphs/ApiNATOMY/models/stomach-spleen.ttl#stomach-spleen'),
# rdflib.term.BNode('ncad49b8b5e044087a11c56ffc9d5f55db1'),
#
# rdflib.term.URIRef('http://celldl.org/templates/vascular#segment-template'
#===============================================================================

NS_MAP = (NamespaceMap.fromSparqlPrefixes(TEMPLATE_PREFIXES)
                      .merge_namespaces(NamespaceMap.fromSparqlPrefixes(MODEL_PREFIXES)))

#===============================================================================

def bg_spec_to_networkx(bg_spec: str) -> nx.DiGraph:
    g = rdflib.Graph(identifier=f'{Path(bg_spec).as_uri()}')
    g.parse(bg_spec, format='turtle')
    NS_MAP.add_namespace('', f'{g.identifier}#')
    G = nx.DiGraph()
    qres: rdflib.query.Result = g.query(MODEL_QUERY)
    if qres.vars is not None:
        model = None
        component = None
        input_node = None
        output_node = None
        (model_key, component_key, template_key, port_key, node_key) = qres.vars
        for row in qres.bindings:
            if model is None:
                model = row[model_key]    ## BondgraphModel()   with addTemplate, etc
                                  ## and template in fact determines graph structure between its ports
                component = row[component_key]
                input_node = None
                output_node = None
            elif model != row[model_key]:
                print('Multiple models...')
                break
            if component != row[component_key]:
                if input_node is not None and output_node is not None:
                    G.add_edge(input_node, output_node)
                component = row[component_key]
                input_node = None
                output_node = None
            port = NS_MAP.curie(row[port_key])
            node = NS_MAP.curie(row[node_key])[1:]
            G.add_node(node, label=node)
            ## need template's defn to know about in/out ports...
            if port == 'lib:blood-pressure_1':
                input_node = node
            elif port == 'lib:blood-pressure_2':
                output_node = node
        if input_node is not None and output_node is not None:
            G.add_edge(input_node, output_node)
    return G

#===============================================================================

if __name__ == '__main__':

    G = bg_spec_to_networkx('/Users/dbro078/CellDL/Bondgraphs/ApiNATOMY/models/stomach-spleen.ttl')

    print(list(G.edges))

#===============================================================================
