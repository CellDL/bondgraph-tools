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

from .queries import TEMPLATE_QUERY, TEMPLATE_PARAMETERS_QUERY, TEMPLATE_PORTS_QUERY, TEMPLATE_STATES_QUERY
from .queries import PORTS_QUERY, PORT_CLASSES_QUERY, PORT_PARAMETERS_QUERY, PORT_STATES_QUERY
from .queries import QUANTITIES_QUERY

#===============================================================================

from .queries import MODEL_PREFIXES, TEMPLATE_PREFIXES
from .namespaces import NamespaceMap

NS_MAP = (NamespaceMap.fromSparqlPrefixes(TEMPLATE_PREFIXES)
                      .merge_namespaces(NamespaceMap.fromSparqlPrefixes(MODEL_PREFIXES)))

#===============================================================================
"""

NB.need full URIRef in order to compare and lookup templates

['template', 'label', 'model', 'parameter']
('lib:segment-template', 'Vascular segment template', 'lib:segment-bondgraph', 'lib:resistance')


['template', 'model', 'port']
('lib:segment-template', 'lib:segment-bondgraph', 'lib:blood-pressure_1')
('lib:segment-template', 'lib:segment-bondgraph', 'lib:blood-pressure_2')

['port', 'units', 'label']
('lib:blood-pressure_1', '"kPa"^^cdt:ucumunit', 'Input pressure')
('lib:blood-pressure_2', '"kPa"^^cdt:ucumunit', 'output pressure')

['port', 'cls']
('lib:blood-pressure_1', 'tpl:Port')
('lib:blood-pressure_1', 'bg:ZeroStorageNode')
('lib:blood-pressure_2', 'tpl:Port')
('lib:blood-pressure_2', 'bg:ZeroStorageNode')

['port', 'parameter']
('lib:blood-pressure_1', 'lib:elastance')
('lib:blood-pressure_1', 'lib:fixed-volume')
('lib:blood-pressure_2', 'lib:elastance')
('lib:blood-pressure_2', 'lib:fixed-volume')

['port', 'state']
('lib:blood-pressure_1', 'lib:volume')
('lib:blood-pressure_2', 'lib:volume')


['quantity', 'units', 'label']
('lib:elastance', '"kPa/L"^^cdt:ucumunit', 'Elastance')
('lib:fixed-volume', '"L"^^cdt:ucumunit', 'Fixed volume')
('lib:volume', '"L"^^cdt:ucumunit', 'Volume')
('lib:resistance', '"kPa.s/L"^^cdt:ucumunit', 'Segment resistance')
"""

#===============================================================================

class UcumUnit:
    def __init__(self, units: Literal):
        self.__units = units
        # check datatype == cdt:ucumunit

    def __str__(self):
        return str(self.__units)

#===============================================================================

class BondgraphQuantity:
    def __init__(self, uri: URIRef, units: Literal, label: Optional[Literal]=None):
        self.__uri = uri
        self.__units = UcumUnit(units)
        self.__label = label if label is not None else NS_MAP.curie(uri)

    @property
    def label(self) -> str:
        return str(self.__label)

    @property
    def units(self):
        return str(self.__units)

    @property
    def uri(self):
        return self.__uri

#===============================================================================

class BondgraphPort:
    def __init__(self, uri: URIRef, units: Literal, label: Optional[Literal]=None):
        self.__uri = uri
        self.__units = UcumUnit(units)
        self.__label = label if label is not None else NS_MAP.curie(uri)
        self.__classes: list[URIRef] = []
        self.__parameters: list[BondgraphQuantity] = []
        self.__states: list[BondgraphQuantity] = []

    @property
    def classes(self):
        return self.__classes

    @property
    def label(self) -> str:
        return str(self.__label)

    @property
    def parameters(self):
        return self.__parameters

    @property
    def states(self):
        return self.__states

    @property
    def units(self):
        return str(self.__units)

    @property
    def uri(self):
        return self.__uri

    def add_class(self, cls: URIRef):
    #================================
        self.__classes.append(cls)

    def add_state(self, state: BondgraphQuantity):
    #=============================================
        self.__states.append(state)

    def add_parameter(self, parameter: BondgraphQuantity):
    #=====================================================
        self.__parameters.append(parameter)

#===============================================================================

class BondgraphTemplate:
    def __init__(self, uri: URIRef, model: URIRef, label: Optional[Literal]=None):
        self.__uri = uri
        self.__model = model
        self.__label = label if label is not None else NS_MAP.curie(uri)
        self.__ports: list[BondgraphPort] = []
        self.__parameters: list[BondgraphQuantity] = []
        self.__states: list[BondgraphQuantity] = []

    @property
    def label(self) -> str:
        return str(self.__label)

    @property
    def model(self):
        return self.__model

    @property
    def parameters(self):
        return self.__parameters

    @property
    def ports(self):
        return self.__ports

    @property
    def states(self):
        return self.__states

    @property
    def uri(self):
        return self.__uri

    def add_port(self, port: BondgraphPort):
    #=======================================
        self.__ports.append(port)

    def add_state(self, state: BondgraphQuantity):
    #=============================================
        self.__states.append(state)

    def add_parameter(self, parameter: BondgraphQuantity):
    #=====================================================
        self.__parameters.append(parameter)

#===============================================================================

class TemplateRegistry:
    def __init__(self, template_file: str):
        self.__ports: dict[URIRef, BondgraphPort] = {}
        self.__quantities: dict[URIRef, BondgraphQuantity] = {}
        self.__templates: dict[URIRef, BondgraphTemplate] = {}
        self.load_templates(template_file)

    def load_templates(self, template_file: str):
    #============================================
        rdf_graph = rdflib.Graph()
        rdf_graph.parse(template_file, format='turtle')
        self.__load_quantities(rdf_graph)
        self.__load_ports(rdf_graph)
        self.__load_templates(rdf_graph)

    def get_template(self, template: URIRef) -> Optional[BondgraphTemplate]:
    #=======================================================================
        return self.__templates.get(template)

    def __load_ports(self, rdf_graph: rdflib.Graph):
    #===============================================
        result = rdf_graph.query(PORTS_QUERY)
        if result.vars is not None:
            (uri_key, units_key, label_key) = result.vars
            for row in result.bindings:
                uri: URIRef = row[uri_key]                  # type: ignore
                units: Literal = row.get(units_key)         # type: ignore
                label: Optional[Literal] = row[label_key]   # type: ignore
                self.__ports[uri] = BondgraphPort(uri, units, label)
        result = rdf_graph.query(PORT_CLASSES_QUERY)
        if result.vars is not None:
            (uri_key, class_key) = result.vars
            for row in result.bindings:
                uri: URIRef = row[uri_key]                  # type: ignore
                cls: URIRef = row.get(class_key)            # type: ignore
                if uri in self.__ports:
                    self.__ports[uri].add_class(cls)
        result = rdf_graph.query(PORT_PARAMETERS_QUERY)
        if result.vars is not None:
            (uri_key, parameter_key) = result.vars
            for row in result.bindings:
                uri: URIRef = row[uri_key]                  # type: ignore
                parameter: URIRef = row.get(parameter_key)  # type: ignore
                if uri in self.__ports and parameter in self.__quantities:
                    self.__ports[uri].add_parameter(self.__quantities[parameter])
        result = rdf_graph.query(PORT_STATES_QUERY)
        if result.vars is not None:
            (uri_key, state_key) = result.vars
            for row in result.bindings:
                uri: URIRef = row[uri_key]                  # type: ignore
                state: URIRef = row.get(state_key)          # type: ignore
                if uri in self.__ports and state in self.__quantities:
                    self.__ports[uri].add_state(self.__quantities[state])

    def __load_quantities(self, rdf_graph: rdflib.Graph):
    #====================================================
        result = rdf_graph.query(QUANTITIES_QUERY)
        if result.vars is not None:
            (uri_key, units_key, label_key) = result.vars
            for row in result.bindings:
                uri: URIRef = row[uri_key]                  # type: ignore
                units: Literal = row.get(units_key)         # type: ignore
                label: Optional[Literal] = row[label_key]   # type: ignore
                self.__quantities[uri] = BondgraphQuantity(uri, units, label)

    def __load_templates(self, rdf_graph: rdflib.Graph):
    #===================================================
        qres = rdf_graph.query(TEMPLATE_QUERY)
        if qres.vars is not None:
            (uri_key, model_key, label_key) = qres.vars
            for row in qres.bindings:
                uri: URIRef = row[uri_key]                  # type: ignore
                model: URIRef = row[model_key]              # type: ignore
                label: Optional[Literal] = row[label_key]   # type: ignore
                self.__templates[uri] = BondgraphTemplate(uri, model, label)
        result = rdf_graph.query(TEMPLATE_PARAMETERS_QUERY)
        if result.vars is not None:
            (uri_key, parameter_key) = result.vars
            for row in result.bindings:
                uri: URIRef = row[uri_key]                 # type: ignore
                parameter: URIRef = row.get(parameter_key)          # type: ignore
                if uri in self.__templates and parameter in self.__quantities:
                    self.__templates[uri].add_parameter(self.__quantities[parameter])
        result = rdf_graph.query(TEMPLATE_PORTS_QUERY)
        if result.vars is not None:
            (uri_key, port_key) = result.vars
            for row in result.bindings:
                uri: URIRef = row[uri_key]                 # type: ignore
                port: URIRef = row.get(port_key)           # type: ignore
                if uri in self.__templates and port in self.__ports:
                    self.__templates[uri].add_port(self.__ports[port])
        result = rdf_graph.query(TEMPLATE_STATES_QUERY)
        if result.vars is not None:
            (uri_key, state_key) = result.vars
            for row in result.bindings:
                uri: URIRef = row[uri_key]                  # type: ignore
                state: URIRef = row.get(state_key)          # type: ignore
                if uri in self.__templates and state in self.__quantities:
                    self.__templates[uri].add_state(self.__quantities[state])

#===============================================================================
