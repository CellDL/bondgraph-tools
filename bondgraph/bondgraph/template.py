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

from typing import Optional

#===============================================================================

import rdflib
from rdflib import Literal, URIRef

#===============================================================================

from .bondgraph import BondgraphModel, BondgraphNode
from .definitions import NS_MAP
from .quantity import Quantity
from .queries import BONDGRAPH_MODEL_BONDS, BONDGRAPH_MODEL_QUANTITIES, BONDGRAPH_MODEL_QUERY
from .queries import TEMPLATE_QUERY, TEMPLATE_PORTS_QUERY
from .queries import QUANTITIES_QUERY

#===============================================================================

class BondgraphTemplate:
    def __init__(self, uri: URIRef, model: Optional[BondgraphModel], label: Optional[Literal]=None):
        self.__uri = uri
        self.__model = model
        self.__label = label if label is not None else NS_MAP.curie(uri)
        self.__ports: dict[URIRef, BondgraphNode] = {}

    def label(self) -> Optional[str]:
        return str(self.__label) if self.__label else None

    @property
    def model(self):
        return self.__model

    @property
    def ports(self):
        return self.__ports

    @property
    def uri(self):
        return self.__uri

    def add_port(self, node_uri: URIRef):
    #====================================
        if self.model is not None and (node := self.model.get_node(node_uri)) is not None:
            self.__ports[node_uri] = node

#===============================================================================

class TemplateRegistry:
    def __init__(self, template_file: str):
        self.__models: dict[URIRef, BondgraphModel] = {}
        self.__quantities: dict[URIRef, Quantity] = {}
        self.__templates: dict[URIRef, BondgraphTemplate] = {}
        self.load_templates(template_file)

    def load_templates(self, template_file: str):
    #============================================
        rdf_graph = rdflib.Graph()
        rdf_graph.parse(template_file, format='turtle')
        self.__load_quantities(rdf_graph)
        self.__load_models(rdf_graph)
        self.__load_templates(rdf_graph)

    def get_template(self, template: URIRef) -> Optional[BondgraphTemplate]:
    #=======================================================================
        return self.__templates.get(template)

    def __load_models(self, rdf_graph: rdflib.Graph):
    #================================================
        result = rdf_graph.query(BONDGRAPH_MODEL_QUERY)
        if result.vars is not None:
            (model_key, node_key, type_key, units_key, label_key) = result.vars[0:5]
            model = None
            for row in result.bindings:
                model_uri: URIRef = row[model_key]          # type: ignore
                node_uri: URIRef = row[node_key]            # type: ignore
                type: URIRef = row[type_key]                # type: ignore
                units: Literal = row.get(units_key)         # type: ignore
                label: Optional[Literal] = row.get(label_key)   # type: ignore
                properties = {str(k): NS_MAP.simplify(row[k]) for k in result.vars[5:] if k in row}
                if type is not None:
                    properties['type'] = NS_MAP.curie(type)
                if model is None or model_uri != model.uri:
                    model = BondgraphModel(model_uri, NS_MAP)
                    self.__models[model_uri] = model
                    model_uri = model.uri
                model.add_node(node_uri, type, units, label=label, properties=properties)
        result = rdf_graph.query(BONDGRAPH_MODEL_BONDS)
        if result.vars is not None:
            (model_key, bond_key, source_key, target_key) = result.vars
            for row in result.bindings:
                model_uri: URIRef = row[model_key]          # type: ignore
                bond_uri: URIRef = row[bond_key]            # type: ignore
                source_uri: URIRef = row[source_key]        # type: ignore
                target_uri: URIRef = row[target_key]        # type: ignore
                if (model := self.__models.get(model_uri)) is not None:
                    model.add_bond(bond_uri, source_uri, target_uri)
        result = rdf_graph.query(BONDGRAPH_MODEL_QUANTITIES)
        if result.vars is not None:
            (model_key, node_key, quantity_key) = result.vars
            for row in result.bindings:
                model_uri: URIRef = row[model_key]          # type: ignore
                node_uri: URIRef = row[node_key]            # type: ignore
                quantity: URIRef = row.get(quantity_key)    # type: ignore
                if (model := self.__models.get(model_uri)) is not None:
                    if ((node := model.get_node(node_uri)) is not None
                     and quantity in self.__quantities):
                        node.add_quantity(self.__quantities[quantity])

    def __load_quantities(self, rdf_graph: rdflib.Graph):
    #====================================================
        result = rdf_graph.query(QUANTITIES_QUERY)
        if result.vars is not None:
            (uri_key, units_key, variable_key, label_key) = result.vars
            for row in result.bindings:
                uri: URIRef = row[uri_key]                  # type: ignore
                units: Literal = row.get(units_key)         # type: ignore
                label: Optional[Literal] = row.get(label_key)   # type: ignore
                variable: Optional[Literal] = row.get(variable_key)   # type: ignore
                self.__quantities[uri] = Quantity(uri, units, label, variable)

    def __load_templates(self, rdf_graph: rdflib.Graph):
    #===================================================
        qres = rdf_graph.query(TEMPLATE_QUERY)
        if qres.vars is not None:
            (uri_key, model_key, label_key) = qres.vars
            for row in qres.bindings:
                uri: URIRef = row[uri_key]                  # type: ignore
                model_uri: URIRef = row[model_key]          # type: ignore
                label: Optional[Literal] = row.get(label_key)   # type: ignore
                self.__templates[uri] = BondgraphTemplate(uri, self.__models.get(model_uri), label)
        result = rdf_graph.query(TEMPLATE_PORTS_QUERY)
        if result.vars is not None:
            (uri_key, node_key) = result.vars
            for row in result.bindings:
                uri: URIRef = row[uri_key]                 # type: ignore
                node: URIRef = row.get(node_key)           # type: ignore
                if (template := self.__templates.get(uri)) is not None:
                    template.add_port(node)

#===============================================================================
