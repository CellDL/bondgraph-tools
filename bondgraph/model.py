#===============================================================================

import logging
from pathlib import Path
from typing import Optional, Self

#===============================================================================

import networkx as nx

import rdflib
from rdflib import Literal, URIRef

#===============================================================================

from .queries import MODEL_QUERY, MODEL_PREFIXES, TEMPLATE_PREFIXES
from .namespaces import NamespaceMap

#===============================================================================

NS_MAP = (NamespaceMap.fromSparqlPrefixes(TEMPLATE_PREFIXES)
                      .merge_namespaces(NamespaceMap.fromSparqlPrefixes(MODEL_PREFIXES)))

#===============================================================================


#===============================================================================




#===============================================================================

class BondgraphConnection:
    def __init__(self, port: str, node: str):
        self.__ports = [port]
        self.__node = node

    def add_port(self, port: str):
    #=============================
        self.__ports.append(port)

#===============================================================================

class BondgraphComponent:
    def __init__(self, id: str, template: str):
        self.__id = id
        self.__connections_by_node: dict[str, BondgraphConnection] = {}

    @property
    def id(self):
        return self.__id

    def add_connection(self, port, node):
    #====================================
        if node in self.__connections_by_node[node]:
            self.__connections_by_node[node].add_port(port)
        else:
            connection = BondgraphConnection(port, node)
            self.__connections_by_node[node] = connection
        #port = NS_MAP.curie(port)       # lib:blood-pressure_1/2
        #node = NS_MAP.curie(node)[1:]   # u_Aorta etc


#===============================================================================

class BondgraphModel:
    def __init__(self, id: str):
        self.__id = id
        self.__components: dict[str, BondgraphComponent] = {}

    @property
    def id(self):
        return self.__id

# Have component (C) with template and connections, where a connection specifies a template port
# and a node with which to identify the connection.

    @classmethod
    def ModelFromRdf(cls, rdf_graph: rdflib.Graph) -> Optional[Self]:
    #================================================================
        self = None
        qres: rdflib.query.Result = rdf_graph.query(MODEL_QUERY)

        NS_MAP.add_namespace('', f'{rdf_graph.identifier}#')

        if qres.vars is not None:
            print([str(k) for k in qres.vars])
            for row in qres:   #  ?template ?label ?model ?parameter
                print(tuple(NS_MAP.simplify(v) for v in row))

            # ?model ?component ?template ?port ?node
            (model_key, component_key, template_key, port_key, node_key) = qres.vars
            component = None
            for row in qres.bindings:
                if self is None:
                    self = cls(row[model_key])
                    component = self.__add_component(row[component_key], row[template_key])
                elif self.__id != row[model_key]:
                    logging.error(f'Multiple models in source, `{self.__id}` used')
                    break
                if component.id != row[component_key]:                      # type: ignore
                    component = self.__add_component(row[component_key], row[template_key])
                component.add_connection(row[port_key], row[node_key])      # type: ignore
        return self

    def __add_component(self, id: str, template: str) -> BondgraphComponent:
    #=======================================================================
        component = BondgraphComponent(id, template)
        self.__components[component.id] = component
        return component


#===============================================================================

def load_model(bg_spec: str) -> Optional[BondgraphModel]:
#========================================================
    g = rdflib.Graph(identifier=f'{Path(bg_spec).as_uri()}')
    g.parse(bg_spec, format='turtle')

    return BondgraphModel.ModelFromRdf(g)

#===============================================================================

"""
:stomach-spleen
    a bg:Model ;
    bg:component [
        tpl:template lib:segment-template ;
        tpl:connection [
            tpl:port lib:blood-pressure_1 ;
            bg:node :u_Aorta
        ], [
            tpl:port lib:blood-pressure_2 ;
            bg:node :u_CeliacA
        ] ;
        bg:parameter [
            bg:name lib:resistance ;
            bg:value "100 kPa.s/L"^^cdt:ucum
        ]
    ], [


?model ?component ?template ?port ?node
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b1', 'lib:segment-template', 'lib:blood-pressure_1', ':u_Aorta')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b1', 'lib:segment-template', 'lib:blood-pressure_2', ':u_CeliacA')

(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b5', 'lib:segment-template', 'lib:blood-pressure_1', ':u_CeliacA')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b5', 'lib:segment-template', 'lib:blood-pressure_2', ':u_GastricC')

(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b9', 'lib:segment-template', 'lib:blood-pressure_1', ':u_CeliacA')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b9', 'lib:segment-template', 'lib:blood-pressure_2', ':u_SplenicC')

(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b13', 'lib:segment-template', 'lib:blood-pressure_1', ':u_GastricC')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b13', 'lib:segment-template', 'lib:blood-pressure_2', ':u_PortalV')

(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b17', 'lib:segment-template', 'lib:blood-pressure_1', ':u_SplenicC')
(':stomach-spleen', 'nb87eb1c10977496a99ee381a8d6dc184b17', 'lib:segment-template', 'lib:blood-pressure_2', ':u_PortalV')


Have component (C) with template and connections, where a connection specifies a template port
and a node with which to identify the connection.

                                C              C
                               --- u_GastricC ---
                 C           /                    \
     -- u_Aorta --- u_CeliacA                      u_PortalV --
                             \\                    /
                               --- u_SplenicC ---
                                C              C


C ==>  --> U --> V --> U -->


                             --> G --> V --> P -->
                 --> C --> V --> G -->
     --> A --> V --> C -->
                 --> C --> V --> S -->
                             --> S --> V --> P -->



                         - V --> G -->
                        /              V
     --> A --> V --> C                   --> P -->
                      \\               V
                        -- V --> S -->





v_in ---> U_node1 --> V_segment --> U_node2 ---> v_out

"""

#===============================================================================
