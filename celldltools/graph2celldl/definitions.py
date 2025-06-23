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

EM_SIZE = 12                    # Pixels, sets ``font-size`` in CellDLStylesheet
INTERFACE_PORT_RADIUS = 4       # pixels

CONNECTION_STROKE_WIDTH = 2

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

class StyleDefinitions:
    def __init__(self, connection_stroke_width: int=CONNECTION_STROKE_WIDTH):
        self.__connection_stroke_width = connection_stroke_width

    @property
    def CellDLStylesheet(self) -> str:
    #=================================
        ### update with any changes ex CellDL editor
        return '\n'.join([    # Copied from ``@renderer/styles/stylesheet.ts``
            f'svg{{font-size:{EM_SIZE}px}}',
            # Components
            '.celldl-Component{fill:#0C4;opacity:0.8;stroke:#44F;rx:6px;ry:6px}',
            '.celldl-Component>text{fill:#C00;opacity:1;stroke:none;text-anchor:middle;dominant-baseline:middle}',
            # Conduits
            '.celldl-Conduit{z-index:9999}',
            # Connections
            f'.celldl-Connection{{stroke-width:{self.__connection_stroke_width};opacity:0.7;fill:none;stroke:currentcolor}}',
            '.celldl-Connection.dashed{stroke-dasharray:5}',
            # Compartments
            '.celldl-Compartment>rect.compartment{fill:#CCC;opacity:0.6;stroke:#444;rx:10px;ry:10px}',
            # Interfaces
            f'.celldl-InterfacePort{{fill:red;r:{INTERFACE_PORT_RADIUS}px}}',
            f'.celldl-Unconnected{{fill:red;fill-opacity:0.1;stroke:red;r:{INTERFACE_PORT_RADIUS}px}}'
        ])


    @property
    def BondgraphSvgDefinitions(self) -> list[etree.Element]:
    #========================================================
        return etree.fromstring(
            '\n'.join([
                f'<defs xmlns="{SVG_NS}">',
                self.__bondgraph_arrow_definition('bondgraph'),
                self.__bondgraph_arrow_definition('biochemical'),
                self.__bondgraph_arrow_definition('electrical'),
                self.__bondgraph_arrow_definition('hydraulic'),
                self.__bondgraph_arrow_definition('mechanical'),
                '</defs>'
            ])
        ).getchildren()

    @property
    def BondgraphStylesheet(self) -> str:
    #====================================
        ### update with arrow changes
        return '\n'.join([
            # Bondgraph specific
            'svg{--biochemical:#2F6EBA;--electrical:#DE8344;--hydraulic:#0A5AB2;--mechanical:#4EAD5B}',
            '.biochemical{color:var(--biochemical)}',
            '.electrical{color:var(--electrical)}',
            '.hydraulic{color:var(--hydraulic)}',
            '.mechanical{color:var(--mechanical)}',
            # use var(--colour), setting them in master stylesheet included in <defs> (along with MathJax styles) */
            '.celldl-Connection.bondgraph.arrow{marker-end:url(#connection-end-arrow-bondgraph)}',
            '.celldl-Connection.bondgraph.biochemical.arrow{marker-end:url(#connection-end-arrow-biochemical)}',
            '.celldl-Connection.bondgraph.electrical.arrow{marker-end:url(#connection-end-arrow-electrical)}',
            '.celldl-Connection.bondgraph.hydraulic.arrow{marker-end:url(#connection-end-arrow-hydraulic)}',
            '.celldl-Connection.bondgraph.mechanical.arrow{marker-end:url(#connection-end-arrow-mechanical)}'
        ])

    ## need to update...
    def __arrow_marker_definition(self, markerId: str, markerType: str) -> str:
    #==========================================================================
        scale = self.__connection_stroke_width/CONNECTION_STROKE_WIDTH
        # see https://developer.mozilla.org/en-US/docs/Web/SVG/Element/marker
        return f"""<marker id="{markerId}" viewBox="0 0 {scale*10} {scale*10}" class="{markerType}"
refX="{scale*6}" refY="{scale*5}" markerWidth="{scale*6}" markerHeight="{scale*6}"
orient="auto-start-reverse" markerUnits="userSpaceOnUse">
        <path fill="currentcolor" stroke="currentcolor" d="M 0 0 L {scale*10} {scale*5} L 0 {scale*10} z" />
    </marker>"""

    def __bondgraph_arrow_definition(self, domain: str) -> str:
    #==========================================================
        return self.__arrow_marker_definition(f'connection-end-arrow-{domain}', domain)

#===============================================================================
#===============================================================================
