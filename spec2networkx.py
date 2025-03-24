#===============================================================================

from pathlib import Path
from typing import Optional

#===============================================================================

import networkx as nx
import rdflib

#===============================================================================

from .queries import MODEL_QUERY

#===============================================================================

class SparqlQuery:
    def __init__(self, query: str, prefixes: Optional[list[str]]=None):
        self.__query = f'{"\n".join(prefixes) if prefixes is not None else ''}{query}'
        self.__prefix_dict = {}
        for line in self.__query.split('\n'):
            if line.strip() == '':
                continue
            elif not self.__define_prefix(line):
                break

    def query(self, g: rdflib.Graph) -> list[tuple[str, ...]]:
    #=========================================================
        result = g.query(self.__query)
        return [tuple(self.__simplify(v) for v in row)
            for row in result]

    def __curie(self, v):
    #====================
        uri = str(v)
        for prefix, namespace in self.__prefix_dict.items():
            if uri.startswith(namespace):
                return f'{prefix}:{uri[len(namespace):]}'
        return uri

    def __define_prefix(self, line):
    #===============================
        parts = line.split()
        if (len(parts) == 3 and parts[0].lower() == 'prefix'
        and parts[1][-1] == ':'
        and parts[2][0] == '<' and parts[2][-1] == '>'):
            self.__prefix_dict[parts[1][:-1]] = parts[2][1:-1]
            return True

    def __simplify(self, v):
    #=======================
        if isinstance(v, rdflib.term.URIRef):
            return self.__curie(v)
        return str(v)

#===============================================================================

# (rdflib.term.URIRef('file:///Users/dbro078/CellDL/Bondgraphs/ApiNATOMY/models/stomach-spleen.ttl#stomach-spleen'),
# rdflib.term.BNode('ncad49b8b5e044087a11c56ffc9d5f55db1'),
#
# rdflib.term.URIRef('http://celldl.org/templates/vascular#segment-template'
#===============================================================================

def bg_spec_to_networkx(bg_spec: str) -> nx.DiGraph:
    g = rdflib.Graph()
    g.parse(bg_spec, format='turtle')

    model_query = SparqlQuery(MODEL_QUERY, prefixes=[f'PREFIX : <{Path(bg_spec).as_uri()}#>'])
    qres = model_query.query(g)

    G = nx.DiGraph()

    model = None

    component = None
    input_port = None
    output_port = None
    for row in qres:
        if model is None:
            model = row[0]    ## BondgraphModel()   with addTemplate, etc
                              ## and template in fact determines graph structure between its ports
            component = row[1]
            input_port = None
            output_port = None
        elif model != row[0]:
            print('Multiple')
            break
        if component != row[1]:
            if input_port is not None and output_port is not None:
                G.add_edge(input_port, output_port)
            component = row[1]
            input_port = None
            output_port = None
        port = row[4][1:]
        G.add_node(port, label=port)
        ## need template's defn to know about in/out ports...
        if row[3] == 'lib:blood-pressure_1':
            input_port = port
        elif row[3] == 'lib:blood-pressure_2':
            output_port = port
    if input_port is not None and output_port is not None:
        G.add_edge(input_port, output_port)
    return G

"""
?model ?component ?template ?port ?node
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b1', 'lib:segment-template', 'lib:blood-pressure_1', ':u_Aorta')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b1', 'lib:segment-template', 'lib:blood-pressure_2', ':u_CeliacA')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b13', 'lib:segment-template', 'lib:blood-pressure_1', ':u_GastricC')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b13', 'lib:segment-template', 'lib:blood-pressure_2', ':u_PortalV')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b17', 'lib:segment-template', 'lib:blood-pressure_1', ':u_SplenicC')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b17', 'lib:segment-template', 'lib:blood-pressure_2', ':u_PortalV')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b5', 'lib:segment-template', 'lib:blood-pressure_1', ':u_CeliacA')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b5', 'lib:segment-template', 'lib:blood-pressure_2', ':u_GastricC')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b9', 'lib:segment-template', 'lib:blood-pressure_1', ':u_CeliacA')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b9', 'lib:segment-template', 'lib:blood-pressure_2', ':u_SplenicC')
"""

#===============================================================================

if __name__ == '__main__':

    G = bg_spec_to_networkx('/Users/dbro078/CellDL/Bondgraphs/ApiNATOMY/models/stomach-spleen.ttl')

    print(list(G.edges))

#===============================================================================
