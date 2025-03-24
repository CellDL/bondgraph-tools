import lxml.etree as etree

#===============================================================================

class XmlNamespace:
    def __init__(self, ns: str):
        self.__ns = ns

    def __str__(self):
        return self.__ns

    def __call__(self, attr: str='') -> str:
        return f'{{{self.__ns}}}{attr}'

#===============================================================================

SVG_NS = XmlNamespace('http://www.w3.org/2000/svg')

#===============================================================================

def svg_element(tag: str, *args, **attributes) -> etree.Element:
#===============================================================
    return etree.Element(SVG_NS(tag), *args, **attributes)

def svg_subelement(parent: etree.Element, tag: str, *args, **attributes) -> etree.Element:
#=========================================================================================
    return etree.SubElement(parent, SVG_NS(tag), *args, **attributes)

#===============================================================================

EM_SIZE = 16                    # Pixels, sets ``font-size`` in CellDLStylesheet
INTERFACE_PORT_RADIUS = 4       # pixels

#===============================================================================

ERROR_COLOUR = 'yellow'

#===============================================================================

DIAGRAM_LAYER = 'diagram-layer'

CELLDL_BACKGROUND_CLASS = 'celldl-background'
CELLDL_LAYER_CLASS = 'celldl-Layer'

CELLDL_DEFINITIONS_ID = "celldl-svg-definitions"
CELLDL_METADATA_ID = "celldl-rdf-metadata"
CELLDL_STYLESHEET_ID = 'celldl-svg-stylesheet'

#===============================================================================

### update with any changes

CellDLStylesheet = '\n'.join([    # Copied from ``@renderer/styles/stylesheet.ts``
    f'svg{{font-size:{EM_SIZE}px}}',
    # Components
    '.celldl-Component{fill:#0C4;opacity:0.8;stroke:#44F;rx:6px;ry:6px}',
    '.celldl-Component>text{fill:#C00;opacity:1;stroke:none;text-anchor:middle;dominant-baseline:middle}',
    # Conduits
    '.celldl-Conduit{z-index:9999}',
    # Connections
    '.celldl-Connection{stroke-width:2;opacity:0.7;fill:none;stroke:currentcolor}',
    '.celldl-Connection.dashed{stroke-dasharray:5}',
    # Compartments
    '.celldl-Compartment>rect.compartment{fill:#CCC;opacity:0.6;stroke:#444;rx:10px;ry:10px}',
    # Interfaces
    f'.celldl-InterfacePort{{fill:red;r:{INTERFACE_PORT_RADIUS}px}}',
    f'.celldl-Unconnected{{fill:red;fill-opacity:0.1;stroke:red;r:{INTERFACE_PORT_RADIUS}px}}'
])

#===============================================================================

## need to update...

def arrow_marker_definition(markerId: str, markerType: str) -> str:
#==================================================================
    # see https://developer.mozilla.org/en-US/docs/Web/SVG/Element/marker
    return f"""<marker id="{markerId}" viewBox="0 0 10 10" class="{markerType}"
refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
    <path fill="currentcolor" stroke="currentcolor" d="M 0 0 L 10 5 L 0 10 z" />
</marker>"""

#===============================================================================
#===============================================================================

def bondgraph_arrow_definition(domain: str) -> str:
#==================================================
    return arrow_marker_definition(f'connection-end-arrow-{domain}', domain)

#===============================================================================

BondgraphSvgDefinitions: list[etree.Element] = etree.fromstring(
    '\n'.join([
        f'<defs xmlns="{SVG_NS}">',
        bondgraph_arrow_definition('bondgraph'),
        bondgraph_arrow_definition('mechanical'),
        bondgraph_arrow_definition('electrical'),
        bondgraph_arrow_definition('biochemical'),
        '</defs>'
    ])
).getchildren()

#===============================================================================

### update with arrow changes

BondgraphStylesheet = '\n'.join([
    # Bondgraph specific
    'svg{--biochemical:#2F6EBA;--electrical:#DE8344;--mechanical:#4EAD5B}',
    '.biochemical{color:var(--biochemical)}',
    '.electrical{color:var(--electrical)}',
    '.mechanical{color:var(--mechanical)}',
    # use var(--colour), setting them in master stylesheet included in <defs> (along with MathJax styles) */
    '.celldl-Connection.bondgraph.arrow{marker-end:url(#connection-end-arrow-bondgraph)}',
    '.celldl-Connection.bondgraph.biochemical.arrow{marker-end:url(#connection-end-arrow-biochemical)}',
    '.celldl-Connection.bondgraph.electrical.arrow{marker-end:url(#connection-end-arrow-electrical)}',
    '.celldl-Connection.bondgraph.mechanical.arrow{marker-end:url(#connection-end-arrow-mechanical)}'
])

#===============================================================================
