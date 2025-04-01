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
from typing import Optional

#===============================================================================

import rdflib
from rdflib import BNode, Literal, URIRef

#===============================================================================

from .bondgraph import BondgraphModel
from .definitions import NS_MAP
from .queries import SPECIFICATION_QUERY, SPECIFICATION_NODE_QUANTITIES, SPECIFICATION_NODE_VALUES
from .template import TemplateRegistry

#===============================================================================

class ModelLoader:
    def __init__(self, bg_spec: str, registry: TemplateRegistry):
        self.__rdf_graph = rdflib.Graph(identifier=f'{Path(bg_spec).absolute().as_uri()}')
        self.__rdf_graph.parse(bg_spec, format='turtle')
        self.__model = None
        self.__model
        self.__ns_map = NS_MAP.copy()
        self.__ns_map.add_namespace('', f'{self.__rdf_graph.identifier}#')
        self.__sparql_prefixes = self.__ns_map.sparql_prefixes()
        self.__load_model(registry)
        if self.__model is not None:
            self.__load_values()
            self.__load_quantities()
            self.__model.freeze()

    @property
    def model(self):
    #===============
        return self.__model

    def __load_model(self, registry):
    #================================
        result = self.__rdf_graph.query(SPECIFICATION_QUERY)
        if result.vars is not None:
            (model_key, name_key, component_key, template_key, port_key, node_key) = result.vars
            last_component = None
            template = None
            template_ports = {}
            for row in result.bindings:
                uri: URIRef = row[model_key]                    # type: ignore
                component_id: BNode = row[component_key]        # type: ignore
                name: Optional[Literal] = row.get(name_key)     # type: ignore
                template_uri: URIRef = row[template_key]        # type: ignore
                port_uri: URIRef = row[port_key]                # type: ignore
                node_uri: URIRef = row[node_key]                # type: ignore
                if self.__model is None:
                    self.__model = BondgraphModel(uri, self.__ns_map, name=name)
                    self.__model_id = self.__ns_map.curie(self.__model.uri)
                elif self.__model.uri != uri:
                    logging.error(f'Multiple models in source, used: `{self.__model.uri}`')
                    break
                if last_component != component_id:
                    if template is not None and len(template_ports):
                        self.__model.merge_template(template, template_ports)
                    template = registry.get_template(template_uri)
                    template_ports = {}
                    last_component = component_id
                template_ports[port_uri] = node_uri
            if self.__model is not None and template is not None and len(template_ports):
                self.__model.merge_template(template, template_ports)

    def __load_quantities(self):
    #===========================
        if self.__model is not None:
            result = self.__rdf_graph.query(SPECIFICATION_NODE_QUANTITIES
                                                .replace('%MODEL%', self.__model_id)
                                                .replace('%PREFIXES%', self.__sparql_prefixes))
            if result.vars is not None:
                (node_key, quantity_key, name_key, value_key) = result.vars
                for row in result.bindings:
                    print({str(k): self.__ns_map.simplify(v) for k, v in row.items()})  # <<<<<<<<<<<<<
                    node_uri: URIRef = row[node_key]            # type: ignore

                    quantity_uri: URIRef = row[quantity_key]    # type: ignore
                    name: URIRef = row[name_key]                # type: ignore
                    value: Literal = row[value_key]             # type: ignore
                    if (node := self.__model.get_node(node_uri)) is not None:
                        node.set_quantity_value(quantity_uri, name, value)

    def __load_values(self):
    #=======================
        if self.__model is not None:
            result = self.__rdf_graph.query(SPECIFICATION_NODE_VALUES
                                                .replace('%MODEL%', self.__model_id)
                                                .replace('%PREFIXES%', self.__sparql_prefixes))
            if result.vars is not None:
                (node_key, value_key) = result.vars
                for row in result.bindings:
                    node_uri: URIRef = row[node_key]            # type: ignore
                    value: Literal = row[value_key]             # type: ignore
                    if (node := self.__model.get_node(node_uri)) is not None:
                        node.set_value(value)

#===============================================================================

def load_model(bg_spec: str, registry: TemplateRegistry) -> Optional[BondgraphModel]:
#====================================================================================
    model_loader = ModelLoader(bg_spec, registry)
    return model_loader.model

#===============================================================================
