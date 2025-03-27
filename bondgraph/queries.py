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

MODEL_PREFIXES = """
PREFIX bg: <http://celldl.org/ontologies/bond-graph#>
PREFIX cdt: <https://w3id.org/cdt/>
PREFIX lib: <http://celldl.org/templates/vascular#>
PREFIX tpl: <http://celldl.org/ontologies/model-template#>
"""

#===============================================================================

MODEL_QUERY = f"""
{MODEL_PREFIXES}

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

TEMPLATE_PARAMETERS_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?template ?parameter
WHERE {{
    ?template
        a tpl:Template ;
        tpl:parameter ?parameter  .
}}"""

#===============================================================================

TEMPLATE_PORTS_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?template ?port
WHERE {{
    ?template
        a tpl:Template ;
        tpl:port ?port .
}}"""

#===============================================================================

TEMPLATE_STATES_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?template ?state
WHERE {{
    ?template
        a tpl:Template ;
        tpl:state ?state  .
}}"""

#===============================================================================

PORTS_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?port ?units ?label
WHERE {{
    ?port
        a tpl:Port ;
        bg:units ?units .
    OPTIONAL {{ ?port rdfs:label ?label }}
}}
"""

#===============================================================================

PORT_CLASSES_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?port ?cls
WHERE {{
    ?port
        a tpl:Port ;
        a ?cls .
    FILTER(?cls != tpl:Port)
}}"""

#===============================================================================

PORT_PARAMETERS_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?port ?parameter
WHERE {{
    ?port
        a tpl:Port ;
        tpl:parameter ?parameter .
}}"""

#===============================================================================

PORT_STATES_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?port ?state
WHERE {{
    ?port
        a tpl:Port ;
        tpl:state ?state .
}}"""

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
