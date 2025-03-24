#===============================================================================

import rdflib

#===============================================================================

from queries import TEMPLATE_QUERY

#===============================================================================

class UcumUnit:
    pass

class BondgraphPort:
    pass

class BondgraphQuantity:
    pass

#===============================================================================

class BondgraphTemplate:
    def __init__(self, template: str):
        self.__g = rdflib.Graph()
        self.__g.parse(template, format='turtle')
        self.__load_templates()

    def __load_templates(self):
    #==========================
        qres = self.__g.query(TEMPLATE_QUERY)
        for row in qres:
            print(row)

#===============================================================================
