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

SELECT DISTINCT ?template ?label ?model ?parameter
WHERE {{
    ?template
        a tpl:Template ;
        bg:model ?model .
    OPTIONAL {{ ?template rdfs:label ?label }}
    OPTIONAL {{ ?template tpl:parameter ?parameter }}

}}"""

#===============================================================================

TEMPLATE_PORTS_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?template ?model ?port
WHERE {{
    ?template
        a tpl:Template ;
        bg:model ?model ;
        tpl:port ?port .
}}
GROUP BY ?template ?model"""

#===============================================================================

PORTS_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?port ?units ?label
WHERE {{
    ?port
        a tpl:Port ;
        bg:units ?units .
    OPTIONAL {{ ?quantity rdfs:label ?label }}
}}
"""

#===============================================================================

PORT_CLASSES_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?port ?cls
WHERE {{
    ?port a ?cls .
}} GROUP BY ?port"""

#===============================================================================

PORT_PARAMETERS_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?port ?parameter
WHERE {{
    ?port tpl:parameter ?parameter .
}} GROUP BY ?port"""

#===============================================================================

PORT_STATES_QUERY = f"""
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?port ?state
WHERE {{
    ?port tpl:state ?state .
}} GROUP BY ?port"""

#===============================================================================

QUANTITIES_QUERY = """
{TEMPLATE_PREFIXES}

SELECT DISTINCT ?quantity ?units ?label
WHERE {{
    ?quantity
        a bg:Quantity ;
        bg:units ?units .
    OPTIONAL { ?quantity rdfs:label ?label }
}}
"""

#===============================================================================
#===============================================================================
