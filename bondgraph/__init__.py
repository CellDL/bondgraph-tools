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

import logging
from pathlib import Path
from typing import Optional, Self

#===============================================================================

import networkx as nx

import rdflib
from rdflib import BNode, Literal, URIRef

#===============================================================================

from .bondgraph import BondgraphModel
from .namespaces import NamespaceMap
from .queries import SPECIFICATION_QUERY, SPEC_PREFIXES, TEMPLATE_PREFIXES
from .template import TemplateRegistry

#===============================================================================

NS_MAP = (NamespaceMap.fromSparqlPrefixes(TEMPLATE_PREFIXES)
                      .merge_namespaces(NamespaceMap.fromSparqlPrefixes(SPEC_PREFIXES)))

#===============================================================================

def load_model(bg_spec: str, registry: TemplateRegistry) -> Optional[BondgraphModel]:
#=====================================================================================
    rdf_graph = rdflib.Graph(identifier=f'{Path(bg_spec).as_uri()}')
    rdf_graph.parse(bg_spec, format='turtle')

# Have component (C) with template and connections, where a connection specifies a template port
# and a node with which to identify the connection.

    model = None
    NS_MAP.add_namespace('', f'{rdf_graph.identifier}#')
    result: rdflib.query.Result = rdf_graph.query(SPECIFICATION_QUERY)
    if result.vars is not None:
        (model_key, component_key, template_key, port_key, port_key) = result.vars
        last_component = None
        template = None
        segment_ports = {}
        for row in result.bindings:
            uri: URIRef = row[model_key]                    # type: ignore
            component_id: BNode = row[component_key]        # type: ignore
            template_uri: URIRef = row[template_key]        # type: ignore
            port_uri: URIRef = row[port_key]                # type: ignore
            node_uri: URIRef = row[port_key]                # type: ignore
            if model is None:
                model = BondgraphModel(uri)
            elif model.uri != uri:
                logging.error(f'Multiple models in source, used: `{model.uri}`')
                break
            if last_component != component_id:
                if template is not None and len(segment_ports):
                    model.merge_template(template, segment_ports)
                template = registry.get_template(template_uri)
                segment_ports = {}
                last_component = component_id
            segment_ports[port_uri] = node_uri
        if model is not None and template is not None and len(segment_ports):
            model.merge_template(template, segment_ports)
    return model

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

tpl_model = BondgraphModel(template.uri)
v_in = tpl_model.add_node('v_in', 'source')
u_node1 = BondgraphNode('u_node1', 'zero-storage')
v_segment = BondgraphNode('v_segment', 'one-resistance')
u_node2 = BondgraphNode('u_node2', 'zero-storage')
v_out = BondgraphNode('v_out', 'sink')

BondgraphNode(v_in, u_node1)
BondgraphNode(u_node1, v_segment)
BondgraphNode(v_segment, u_node2)
BondgraphNode(u_node2, v_out)

"""

#===============================================================================


