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

import copy
from typing import Any, Optional, Self, TYPE_CHECKING

#===============================================================================

import networkx as nx
from rdflib import Literal, URIRef

#===============================================================================

from .namespaces import NamespaceMap
from .quantity import Quantity, Units, Value
from .definitions import BONDGRAPH_BASE_TYPES

if TYPE_CHECKING:
    from .template import BondgraphTemplate

#===============================================================================

class BondgraphNode:
    def __init__(self, uri: URIRef, type: URIRef, units: Units,
            label: Optional[Literal]=None, properties: Optional[dict[str, Any]]=None):
        self.__uri = uri
        self.__type = type
        self.__units = units
        self.__label = label
        self.__properties = properties if properties is not None else {}
        self.__quantities: dict[URIRef, Quantity] = {}
        self.__quantity_values: dict[URIRef, tuple[URIRef, float]] = {}
        self.__sources: set[BondgraphNode] = set()
        self.__targets: set[BondgraphNode] = set()
        self.__value: Optional[Value] = None

    @property
    def delta(self) -> str:
    #======================
        inputs = '+'.join([n.name for n in self.__sources])
        outputs = '-'.join([n.name for n in self.__targets])
        if inputs != '' and outputs != '':
            return f'{inputs}-{outputs}'
        elif inputs != '':
            return inputs
        elif outputs != '':
            return f'-{outputs}'
        else:
            return ''

    @property
    def label(self) -> Optional[str]:
        return str(self.__label) if self.__label else None

    @property
    def name(self) -> str:
        return self.__uri.rsplit('#')[-1]

    @property
    def properties(self):
        return self.__properties

    @property
    def quantity_values(self) -> list[tuple[Quantity, str, float]]:
        return [(self.__quantities[quantity], name_value[0].rsplit('#')[-1], name_value[1])
                    for quantity, name_value in self.__quantity_values.items()]

    @property
    def sources(self):
        return self.__sources

    @property
    def targets(self):
        return self.__targets

    @property
    def type(self):
        # If a ZeroStorage or OneResistance node hasn't been assigned values for
        # its parameters then it's treated as a Zero or One node.
        if len(self.__quantity_values) == 0:
            return BONDGRAPH_BASE_TYPES.get(self.__type, self.__type)
        else:
            return self.__type

    @property
    def units(self) -> Units:
        return self.__units

    @property
    def uri(self):
        return self.__uri

    @property
    def value(self):
        return self.__value.value if self.__value is not None else None

    def add_quantity(self, quantity: Quantity):
    #==========================================
        self.__quantities[quantity.uri] = quantity

    def add_source(self, source: Self):
    #==================================
        self.__sources.add(source)

    def add_target(self, target: Self):
    #==================================
        self.__targets.add(target)

    def copy(self) -> 'BondgraphNode':
    #=================================
        node = BondgraphNode(self.__uri, self.__type, self.__units,
            label=self.__label, properties=self.__properties.copy())
        node.__quantities = self.__quantities.copy()
        return node

    def get_property(self, key: str, default=None) -> Optional[Any]:
    #===============================================================
        return self.__properties.get(key, default)

    def has_property(self, key: str) -> bool:
    #========================================
        return key in self.__properties

    def set_quantity_value(self, quantity_uri: URIRef, name: URIRef, value: Literal):   # "100 kPa.s/L"^^cdt:ucum
    #================================================================================
        if (quantity := self.__quantities.get(quantity_uri)) is not None:
            new_value = Value(value)
            if new_value.units != quantity.units:
                raise TypeError(f"Value's units don't match Quantity's: {new_value.units} != {quantity.units}")
            self.__quantity_values[quantity_uri] = (name, new_value.value)

    def set_uri(self, uri: URIRef):
    #==============================
        self.__uri = uri

    def set_value(self, value: Literal):   # "100 kPa.s/L"^^cdt:ucum
    #===================================
        new_value = Value(value)
        if new_value.units != self.__units:
            raise TypeError(f"Value's units don't match nodes's: {new_value.units} != {self.__units}")
        if self.__value is None:
            self.__value = new_value
        else:
            self.__value.set_value(new_value.value)

#===============================================================================

class BondgraphBond:
    def __init__(self, uri: URIRef, node_0: BondgraphNode, node_1: BondgraphNode):
        self.__uri = uri
        self.__nodes = (node_0, node_1)
        node_1.add_source(node_0)
        node_0.add_target(node_1)

    @property
    def nodes(self):
        return self.__nodes

    @property
    def uri(self):
        return self.__uri

#===============================================================================

class BondgraphModel:
    def __init__(self, uri: URIRef, ns_map: NamespaceMap, name: Optional[Literal]=None):
        self.__uri = uri
        self.__name = str(name) if name is not None else uri.rsplit('#')[-1]
        self.__ns_map = ns_map
        self.__nodes: dict[URIRef, BondgraphNode] = {}
        self.__bonds: dict[URIRef, BondgraphBond] = {}
        self.__last_id = 0
        self.__updatable  = True
        self.__nx_graph = None

    @property
    def bonds(self) -> list[BondgraphBond]:
    #======================================
        return list(self.__bonds.values())

    @property
    def disconnected(self):
    #======================
        return self.__nx_graph is None or not nx.is_weakly_connected(self.__nx_graph)

    @property
    def frozen(self):
    #================
        return not self.__updatable

    @property
    def name(self):
    #==============
        return self.__name

    @property
    def nodes(self) -> list[BondgraphNode]:
    #======================================
        return list(self.__nodes.values())

    @property
    def uri(self):
    #=============
        return self.__uri

    def add_node(self, node_uri: URIRef, type: URIRef, units: Literal,
    #=================================================================
                 label: Optional[Literal]=None,
                 properties: Optional[dict[str, Any]]=None) -> BondgraphNode:
        self.__check_updatable()
        node = BondgraphNode(node_uri, type, Units.from_ucum(units), label=label, properties=properties)
        self.__nodes[node_uri] = node
        return node

    def add_bond(self, uri: URIRef, node_0: URIRef, node_1: URIRef) -> Optional[BondgraphBond]:
    #==========================================================================================
        self.__check_updatable()
        if ((n0 := self.get_node(node_0)) is not None
        and (n1 := self.get_node(node_1)) is not None):
            bond = BondgraphBond(uri, n0, n1)
            self.__bonds[uri] = bond
            return bond

    def __check_updatable(self):
    #===========================
        if not self.__updatable:
            raise ValueError(f"Bondgraph {self.__uri} is readonly and can't be modified")

    def __create_nx_graph(self):
    #===========================
        if self.__nx_graph is None:
            self.__nx_graph = nx.DiGraph()
            for node in self.__nodes.values():
                node_id = self.__ns_map.curie(node.uri)
                attributes = node.properties.copy()
                attributes['label'] = node_id[1:]
                if node.type is not None:
                    attributes['type'] = self.__ns_map.curie(node.type)
                self.__nx_graph.add_node(node_id, **attributes)
            # Can use a nodes sources/targets...
            for bond in self.__bonds.values():
                self.__nx_graph.add_edge(*[self.__ns_map.curie(node.uri) for node in bond.nodes])

    def freeze(self):
    #================
        if self.__updatable:
            self.__create_nx_graph()
            self.__updatable = False

    def get_node(self, node_uri: URIRef) -> Optional[BondgraphNode]:
    #===============================================================
        return self.__nodes.get(node_uri)

    def has_node(self, node_uri: URIRef) -> bool:
    #============================================
        return node_uri in self.__nodes

    def __get_uri(self) -> URIRef:
    #=============================
        self.__last_id += 1
        return self.__ns_map.uri(f':ID-{self.__last_id:08d}')

    def merge_template(self, template: 'BondgraphTemplate', template_ports: dict[URIRef, URIRef]):
    #=============================================================================================
        self.__check_updatable()
        if template.model is not None:
            uri_remap = {}
            for node in template.model.nodes:
                if node.uri in template_ports:
                    node_uri = template_ports[node.uri]
                else:
                    node_uri = self.__get_uri()
                uri_remap[node.uri] = node_uri
                if node_uri not in self.__nodes:
                    new_node = node.copy()
                    new_node.set_uri(node_uri)
                    self.__nodes[node_uri] = new_node
            for bond in template.model.__bonds.values():
                self.add_bond(self.__get_uri(), uri_remap[bond.nodes[0].uri], uri_remap[bond.nodes[1].uri])

    def nx_graph(self) -> nx.DiGraph:
    #================================
        self.freeze()
        return self.__nx_graph      # type: ignore [return-value]

#===============================================================================


