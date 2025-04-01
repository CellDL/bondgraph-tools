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

from rdflib import URIRef

#===============================================================================

from .queries import SPEC_PREFIXES, TEMPLATE_PREFIXES
from .namespaces import NamespaceMap

NS_MAP = (NamespaceMap.fromSparqlPrefixes(TEMPLATE_PREFIXES)
                      .merge_namespaces(NamespaceMap.fromSparqlPrefixes(SPEC_PREFIXES)))

#===============================================================================

BONDGRAPH_BASE_TYPES: dict[URIRef, URIRef] = {
    NS_MAP.uri('bg:OneResistanceNode'): NS_MAP.uri('bg:OneNode'),
    NS_MAP.uri('bg:ZeroStorageNode'): NS_MAP.uri('bg:ZeroNode'),
}

#===============================================================================

BONDGRAPH_EQUATIONS: dict[URIRef, list[str]] = {
    NS_MAP.uri('bg:ZeroStorageNode'): [
        'Eq(Derivative({CHARGE}, {TIME}), {NODE_DELTA})',
        'Eq({NODE}, {ELASTANCE}*({CHARGE} - {RESIDUAL_CHARGE}))',
    ],
    NS_MAP.uri('bg:OneResistanceNode'): [
        'Eq({NODE}, ({NODE_DELTA})/{RESISTANCE})',
    ],
}

#===============================================================================
