#===============================================================================
#
#  CellDL Editor and tools
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

from datetime import datetime, UTC

#===============================================================================

import rdflib

#===============================================================================

CELLDL_SCHEMA_VERSION = '1.0'

#===============================================================================

DCT_NS = rdflib.Namespace('http://purl.org/dc/terms/')
OWL_NS = rdflib.Namespace('http://www.w3.org/2002/07/owl#')
RDF_NS = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS_NS = rdflib.Namespace('http://www.w3.org/2000/01/rdf-schema#')

#===============================================================================

BG_NS = rdflib.Namespace('http://celldl.org/ontologies/bond-graph#')
CELLDL_NS = rdflib.Namespace('http://celldl.org/ontologies/celldl#')

STANDARD_NAMESPACES = {
    'celldl': CELLDL_NS,
    'dct': DCT_NS,
    'owl': OWL_NS,
}

#===============================================================================

DIAGRAM_NS = rdflib.Namespace('#')

def make_uri(id: str) -> rdflib.URIRef:
    return DIAGRAM_NS[id]

#===============================================================================

class CellDLGraph:
    def __init__(self):
        self.__graph = rdflib.Graph()
        self.__diagram = make_uri('')
        self.__graph.bind('', str(DIAGRAM_NS))
        for (prefix, ns) in STANDARD_NAMESPACES.items():
            self.__graph.bind(prefix, str(ns))
        self.__graph.add((self.__diagram, RDF_NS.type, CELLDL_NS.Document))
        self.__graph.add((self.__diagram, OWL_NS.versionInfo, rdflib.Literal(CELLDL_SCHEMA_VERSION)))
        self.__graph.add((self.__diagram, DCT_NS.created, rdflib.Literal(datetime.now(UTC).isoformat())))

    def add_component(self, id: str):
    #================================
        this = make_uri(id)
        self.__graph.add((this, RDF_NS.type, CELLDL_NS.Component))

    def add_connection(self, id: str, source: str, target: str):
    #===========================================================
        this = make_uri(id)
        self.__graph.add((this, RDF_NS.type, CELLDL_NS.Connection))
        self.__graph.add((this, CELLDL_NS.hasSource, make_uri(source)))
        self.__graph.add((this, CELLDL_NS.hasTarget, make_uri(target)))

    def as_turtle(self) -> bytes:
    #============================
        return self.__graph.serialize(format='turtle', encoding='utf-8')

    def as_xml(self) -> bytes:
    #=========================
        return self.__graph.serialize(format='xml', encoding='utf-8')

    def set_property(self, property: rdflib.URIRef, value: rdflib.Literal|rdflib.URIRef):
    #====================================================================================
        self.__graph.add((self.__diagram, property, value))

#===============================================================================
