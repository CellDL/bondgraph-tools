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

from typing import Optional, TYPE_CHECKING

#===============================================================================

from rdflib import Literal, URIRef

#===============================================================================

from .quantity import Quantity, Units, Value

if TYPE_CHECKING:
    from .template import BondgraphTemplate

#===============================================================================

class BondgraphNode:
    def __init__(self, uri: URIRef, type: URIRef, label: Optional[Literal]=None, units: Optional[Literal]=None):
        self.__uri = uri
        self.__type = type
        self.__label = label
        self.__units = Units.from_ucum(units)
        self.__quantities: dict[URIRef, Quantity] = {}
        self.__quantity_values: dict[URIRef, tuple[URIRef, float]] = {}
        self.__value: Optional[Value] = None

    @property
    def label(self) -> Optional[str]:
        return str(self.__label) if self.__label else None

    @property
    def quantity_values(self) -> list[tuple[Quantity, str, float]]:
        return [(self.__quantities[quantity], name_value[0].rsplit('#')[-1], name_value[1])
                    for quantity, name_value in self.__quantity_values.items()]


    @property

    @property
    def type(self):
        return self.__type

    @property
    def units(self) -> Units:
        return self.__units

    @property
    def uri(self):
        return self.__uri

    def value(self):
        return self.__value.value if self.__value is not None else None

    def add_quantity(self, quantity: Quantity):
    #==========================================
        self.__quantities[quantity.uri] = quantity

    def set_quantity_value(self, quantity_uri: URIRef, name: URIRef, value: Literal):   # "100 kPa.s/L"^^cdt:ucum
    #================================================================================
        if (quantity := self.__quantities.get(quantity_uri)) is not None:
            new_value = Value(value)
            if new_value.units != quantity.units:
                raise TypeError(f"Value's units don't match Quantity's: {new_value.units} != {quantity.units}")
            self.__quantity_values[quantity_uri] = (name, new_value.value)


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

    @property
    def nodes(self):
        return self.__nodes

    @property
    def uri(self):
        return self.__uri

#===============================================================================

class BondgraphModel:
    def __init__(self, uri: URIRef):
        self.__uri = uri
        self.__nodes: dict[URIRef, BondgraphNode] = {}
        self.__bonds: dict[URIRef, BondgraphBond] = {}

    @property
    def uri(self):
        return self.__uri

    def add_node(self, node_uri: URIRef, type: URIRef, label: Optional[Literal]=None, units: Optional[Literal]=None) -> BondgraphNode:
    #=================================================================================================================================
        node = BondgraphNode(node_uri, type, label=label, units=units)
        self.__nodes[node_uri] = node
        return node

    def add_bond(self, uri: URIRef, node_0: BondgraphNode, node_1: BondgraphNode) -> BondgraphBond:
    #==============================================================================================
        bond = BondgraphBond(uri, node_0, node_1)
        self.__bonds[uri] = bond
        return bond

    def get_node(self, node_uri: URIRef) -> Optional[BondgraphNode]:
    #===============================================================
        return self.__nodes.get(node_uri)

    def has_node(self, node_uri: URIRef) -> bool:
    #============================================
        return node_uri in self.__nodes


    def __add_template(self, template, node_uri, port_uri):
        pass

    def merge_template(self, template: 'BondgraphTemplate', template_ports: dict[URIRef, URIRef]):
    #=============================================================================================
        if template.model is not None:
            for port_uri, node_uri in template_ports.items():
                if (port := template.model.get_node(port_uri)) is not None:
                    if (node := self.get_node(node_uri)) is not None:
                        pass
                        # check node and port are compatible (same bondgraphClass)
                    else:
                        self.__add_template(template, node_uri, port)

#===============================================================================


