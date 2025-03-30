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

SPEC_PREFIXES = """
PREFIX bg: <http://celldl.org/ontologies/bond-graph#>
PREFIX cdt: <https://w3id.org/cdt/>
PREFIX lib: <http://celldl.org/templates/vascular#>
PREFIX tpl: <http://celldl.org/ontologies/model-template#>
"""

#===============================================================================

SPECIFICATION_QUERY = f"""
{SPEC_PREFIXES}

SELECT DISTINCT ?model ?component ?template ?port ?node
WHERE {{
    ?model
        a bg:Model ;
        bg:component ?component .
    ?component
        tpl:template ?template ;
        tpl:connection ?connection .
    ?connection
        tpl:port ?port ;
        bg:node ?node .
}}
GROUP BY ?model ?component ?connection
ORDER BY ?model ?component"""

#===============================================================================
#===============================================================================

TEMPLATE_PREFIXES = """
PREFIX : <http://celldl.org/templates/vascular#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX bg: <http://celldl.org/ontologies/bond-graph#>
PREFIX cdt: <https://w3id.org/cdt/>
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

BONDGRAPH_MODEL_PARAMETERS = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?model ?node ?parameter
WHERE {{
    ?model a bg:Model .
    ?node
        a ?type ;
        tpl:parameter ?parameter  .
    FILTER (?type IN (bg:OneResistanceNode, bg:ZeroStorageNode))
}}"""

#===============================================================================

BONDGRAPH_MODEL_STATES = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?model ?node ?state
WHERE {{
    ?model a bg:Model .
    ?node
        a ?type ;
        tpl:state ?state  .
    FILTER (?type IN (bg:OneResistanceNode, bg:ZeroStorageNode))
}}"""

#===============================================================================

BONDGRAPH_MODEL_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?model ?node ?type ?label ?units
WHERE {{
    ?model a bg:Model .
    ?node
        a ?type ;
        bg:model ?model .
    OPTIONAL {{ ?node rdfs:label ?label }}
    OPTIONAL {{ ?node bg:units ?units }}
    FILTER (?type IN (bg:OneResistanceNode, bg:ZeroStorageNode))
}} ORDER BY ?model"""

#===============================================================================
#===============================================================================

QUANTITIES_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?quantity ?units ?label
WHERE {{
    ?quantity
        a bg:Quantity ;
        bg:units ?units .
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
