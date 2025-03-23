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

import json
from pathlib import Path

#===============================================================================

import lxml.etree as etree
import networkx as nx
import numpy as np

#===============================================================================

from .celldl import CellDLGraph

from .definitions import svg_element, svg_subelement, SVG_NS
from .definitions import CELLDL_DEFINITIONS_ID, CELLDL_LAYER_CLASS
from .definitions import CELLDL_METADATA_ID, CELLDL_STYLESHEET_ID, DIAGRAM_LAYER
from .definitions import BondgraphStylesheet, BondgraphSvgDefinitions, CellDLStylesheet

#===============================================================================

SVG_WIDTH = 1200
SVG_HEIGHT = 800

#===============================================================================

LAYOUT_METHODS = {
    'arf': nx.arf_layout,
    'force': nx.forceatlas2_layout,
    'kk': nx.kamada_kawai_layout,
    'planar': nx.planar_layout,
    'spring': nx.spring_layout,
}

#===============================================================================

NODE_SIZE = (100, 70)

NODE_CORNER_RADIUS = 6

#===============================================================================

def _scaled_vertical_offset(x: float, delta: np.ndarray) -> np.ndarray:
#======================================================================
    return np.array([x, x*delta[1]/delta[0]])

def _scaled_horizontal_offset(y: float, delta: np.ndarray) -> np.ndarray:
#========================================================================
    return np.array([y*delta[0]/delta[1], y])

#===============================================================================

class CellDLComponent:
    def __init__(self, id: str, centre: np.ndarray):
        self.__id = id
        self.__centre = centre
        top_left = np.array([centre[0]-NODE_SIZE[0]/2, centre[0]-NODE_SIZE[1]/2])
        bottom_right = np.array([centre[0]+NODE_SIZE[0]/2, centre[0]+NODE_SIZE[1]/2])
        self.__corner_offsets = [
            bottom_right, np.array([top_left[0], bottom_right[1]]),
            top_left, np.array([bottom_right[0], top_left[1]])
        ]

    @property
    def centre(self):
        return self.__centre

    @property
    def id(self):
        return self.__id

    def boundary_intersection(self, point: np.ndarray) -> np.ndarray:
    #================================================================
        #
        # Find where line from point to centre crosses node's boundary
        #
        #                +---dx---+
        #                 \       |
        #                  \      |
        #                   \     |
        #              2  ---\---------------------------  1
        #                |    \   |                      |
        #                |     \  |                      |
        #                |      \ dh                     |
        #                |       \|                      |
        #                |---dw---o                      |
        #              3  -------------------------------  0
        #
        #
        #    TOP         dh/dw     <  dy/dx  <      dh/(w-dw)
        #    RIGHT     dh/(w-dw)                (h-dh)/(w-dw)
        #    BOTTOM  (h-dh)/(w-dw)                (h-dh)/dw
        #    LEFT      (h-dh)/dw                     dh/dw
        #
        #    Four quadrants wrt centroid:
        #
        #    +deltaX, +deltaY     bottom-right corner  BR  0   (w-dw)  (h-dh)
        #    +deltaX, -deltaY     top-right corner     TR  1   (w-dw)   -dh
        #    -deltaX, -deltaY     top-left corner      TL  2    -dw     -dh
        #    -deltaX, +deltaY     bottom-left corner   BL  3    -dw    (h-dh)
        #
        #   Corner offsets are wrt centroid, anticlockwise from bottom right
        #
        #   BR, TR, TL, BL
        #    0   1   2   3
        #
        delta = point - self.__centre
        if delta[0] < 0:
            if delta[1] < 0:    # TL
                if self.__corner_offsets[2][0]*delta[1] < self.__corner_offsets[2][1]*delta[0]:
                    offset = _scaled_vertical_offset(self.__corner_offsets[2][0], delta)
                else:
                    offset = _scaled_horizontal_offset(self.__corner_offsets[2][1], delta)
            else:               # BL
                if self.__corner_offsets[3][0]*delta[1] < self.__corner_offsets[3][1]*delta[0]:
                    offset = _scaled_horizontal_offset(self.__corner_offsets[3][1], delta)
                else:
                    offset = _scaled_vertical_offset(self.__corner_offsets[3][0], delta)
        else:
            if delta[1] < 0:    # TR
                if self.__corner_offsets[1][0]*delta[1] < self.__corner_offsets[1][1]*delta[0]:
                    offset = _scaled_horizontal_offset(self.__corner_offsets[1][1], delta)
                else:
                    offset = _scaled_vertical_offset(self.__corner_offsets[1][0], delta)
            else:               # BR
                if self.__corner_offsets[0][0]*delta[1] < self.__corner_offsets[0][1]*delta[0]:
                    offset = _scaled_vertical_offset(self.__corner_offsets[0][0], delta)
                else:
                    offset = _scaled_horizontal_offset(self.__corner_offsets[0][1], delta)
        return self.__centre + offset

    def svg(self) -> etree.Element:
    #==============================
        return svg_element('rect', {
            'id': self.__id, 'class': 'celldl-Component',
            'x': str(self.__corner_offsets[2][0]), 'y': str(self.__corner_offsets[2][1]),
            'width': str(NODE_SIZE[0]), 'height': str(NODE_SIZE[1]),
            'rx': str(NODE_CORNER_RADIUS), 'ry': str(NODE_CORNER_RADIUS)
        })

#===============================================================================

class Graph2CellDL:
    def __init__(self, G: nx.DiGraph, layout_method: str='arf'):
        self.__celldl = CellDLGraph()
        self.__last_id = 0
        self.__create_diagram()
        self.__positions = nx.rescale_layout_dict(
            LAYOUT_METHODS.get(layout_method, nx.arf_layout)(G),
            scale=min(SVG_WIDTH, SVG_HEIGHT)/2)
        self.__components: dict = {}
        for node, properties in G.nodes(data=True):
            self.__add_component(node, properties)
        for node_0, node_1, properties in G.edges(data=True):
            self.__add_connection(node_0, node_1, properties)

    def __add_connection(self, node_0, node_1, properties):
    #======================================================
        source = self.__components[node_0]
        target = self.__components[node_1]
        source_point = source.boundary_intersection(target.centre)
        target_point = target.boundary_intersection(source.centre)
        connection_id = self.__get_id()
        path = svg_subelement(self.__diagram, 'path', {
            'id': connection_id,
            'class': 'celldl-Connection arrow',
            'd': f'M{source_point[0]} {source_point[1]}L{target_point[0]} {target_point[1]}',
        })
        self.__celldl.add_connection(connection_id, source.id, target.id)

    def __add_component(self, node, properties):
    #===========================================
        component = CellDLComponent(self.__get_id(), self.__positions[node])
        self.__diagram.append(component.svg())
        self.__celldl.add_component(component.id)
        self.__components[node] = component

    def __create_diagram(self):
    #==========================
        self.__svg = svg_element('svg', nsmap={None: str(SVG_NS)},
            viewBox=f'{-int(SVG_WIDTH/2)} {-int(SVG_HEIGHT/2)} {SVG_WIDTH} {SVG_HEIGHT}'
        )
        self.__metadata_element = svg_subelement(self.__svg, 'metadata', {
            'id': CELLDL_METADATA_ID,
            'data-content-type': 'text/turtle'
        })
        defs = svg_subelement(self.__svg, 'defs', {
            'id': CELLDL_DEFINITIONS_ID
        })
        defs.extend(BondgraphSvgDefinitions)
        style = svg_subelement(defs, 'style', {
            'id': CELLDL_STYLESHEET_ID
            })
        stylesheets = [CellDLStylesheet]
        stylesheets.append(BondgraphStylesheet)
        style.text = '\n'.join(stylesheets)
        self.__diagram = svg_subelement(self.__svg, 'g', {
            'id': DIAGRAM_LAYER,
            'class': CELLDL_LAYER_CLASS
        })

    def __get_id(self) -> str:
    #=========================
        self.__last_id += 1
        return f'ID-{self.__last_id:08d}'

    def save_diagram(self, path: Path):
    #==================================
        self.__metadata_element.text = etree.CDATA(self.__celldl.as_turtle())
        svg_tree = etree.ElementTree(self.__svg)
        svg_tree.write(path,
            encoding='utf-8', inclusive_ns_prefixes=['svg'],
            pretty_print=True, xml_declaration=True)

#===============================================================================

def graph2celldl(G: nx.DiGraph, celldl_file: str, layout_method: str='arf'):
    celldl = Graph2CellDL(G, layout_method)
    celldl.save_diagram(Path(celldl_file))

#===============================================================================
