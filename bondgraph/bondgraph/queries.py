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

BONDGRAPH_NODE_TYPES = [
    'bg:OneNode',
    'bg:OneResistanceNode',
    'bg:ResistanceNode',
    'bg:StorageNode',
    'bg:ZeroNode',
    'bg:ZeroStorageNode',
]

#===============================================================================
#===============================================================================

SPEC_PREFIXES = """
PREFIX : <#>
PREFIX bg: <http://celldl.org/ontologies/bond-graph#>
PREFIX cdt: <https://w3id.org/cdt/>
PREFIX lib: <http://celldl.org/templates/vascular#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tpl: <http://celldl.org/ontologies/model-template#>
"""

#===============================================================================

SPECIFICATION_QUERY = f"""
{SPEC_PREFIXES}

SELECT DISTINCT ?model ?name ?component ?template ?port ?node
WHERE {{
    ?model
        a bg:Model ;
        bg:component ?component .
    ?component
        tpl:template ?template ;
        tpl:interface [
            tpl:node ?port ;
            bg:node ?node
        ].
    OPTIONAL {{ ?model rdfs:label ?name }}
}}
ORDER BY ?model ?component"""

#===============================================================================

SPECIFICATION_NODE_QUANTITIES = f"""
%PREFIXES%

SELECT DISTINCT ?node ?quantity ?name ?value
WHERE {{
    %MODEL% bg:component [
        tpl:interface [
            bg:node ?node
        ]
    ] .
    ?node bg:quantities [
        bg:quantity ?quantity ;
        bg:name ?name ;
        bg:value ?value
    ] .
}}
ORDER BY ?node"""

#===============================================================================

SPECIFICATION_NODE_VALUES = f"""
%PREFIXES%

SELECT DISTINCT ?node ?value
WHERE {{
    %MODEL% bg:component [
        tpl:interface [
            bg:node ?node
        ]
    ] .
    ?node bg:value ?value .
}}
ORDER BY ?node"""

#===============================================================================
#===============================================================================

TEMPLATE_PREFIXES = """
PREFIX : <http://celldl.org/templates/vascular#>
PREFIX bg: <http://celldl.org/ontologies/bond-graph#>
PREFIX cdt: <https://w3id.org/cdt/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tpl: <http://celldl.org/ontologies/model-template#>
"""

#===============================================================================

BONDGRAPH_MODEL_BONDS = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?model ?bond ?source ?target
WHERE {{
    ?model a bg:Model .
    ?bond
        a bg:Bond ;
        bg:model ?model ;
        bg:source ?source ;
        bg:target ?target .
}}"""

#===============================================================================

BONDGRAPH_MODEL_QUANTITIES = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?model ?node ?quantity
WHERE {{
    ?model a bg:Model .
    ?node
        a ?type ;
        bg:quantities ?quantity  .
    FILTER (?type IN ({', '.join(BONDGRAPH_NODE_TYPES)}))
}}"""

#===============================================================================

BONDGRAPH_MODEL_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?model ?node ?type ?units ?label ?location ?species
WHERE {{
    ?model a bg:Model .
    ?node
        a ?type ;
        bg:model ?model ;
        bg:units ?units .
    OPTIONAL {{ ?node rdfs:label ?label }}
    OPTIONAL {{ ?node bg:nodeSettings ?ns
        OPTIONAL {{ ?ns bg:location ?location }}
        OPTIONAL {{ ?ns bg:species ?species }}
    }}
    FILTER (?type IN ({', '.join(BONDGRAPH_NODE_TYPES)}))
}} ORDER BY ?model"""

#===============================================================================
#===============================================================================

QUANTITIES_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?quantity ?units ?variable ?label
WHERE {{
    ?quantity
        a bg:Quantity ;
        bg:units ?units .
    OPTIONAL {{ ?quantity bg:variable ?variable }}
    OPTIONAL {{ ?quantity rdfs:label ?label }}
}}"""

#===============================================================================
#===============================================================================

TEMPLATE_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?template ?model ?label
WHERE {{
    ?template
        a tpl:Template ;
        bg:model ?model .
    OPTIONAL {{ ?template rdfs:label ?label }}
}}"""


#===============================================================================

TEMPLATE_PORTS_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?template ?node
WHERE {{
    ?template
        a tpl:Template ;
        tpl:port ?node .
}}"""

#===============================================================================
#===============================================================================
