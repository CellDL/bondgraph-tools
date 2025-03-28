#===============================================================================

from typing import Optional, Self

#===============================================================================

import rdflib

#===============================================================================

class NamespaceMap:
    def __init__(self, ns_map: Optional[dict[str, str]]=None):
        self.__prefix_dict: dict[str, str] = {}
        self.__reverse_map: dict[str, str] = {}
        if ns_map is not None:
            for prefix, namespace in ns_map.items():
                self.add_namespace(prefix, namespace)

    @classmethod
    def fromSparqlPrefixes(cls, query: str) -> Self:
    #===============================================
        ns_map = {}
        for line in query.split('\n'):
            if line.strip() == '':
                continue
            else:
                parts = line.split()
                if (len(parts) == 3 and parts[0].lower() == 'prefix'
                and parts[1][-1] == ':'
                and parts[2][0] == '<' and parts[2][-1] == '>'):
                    ns_map[parts[1][:-1]] = parts[2][1:-1]
                    continue
                break
        return cls(ns_map)

    def add_namespace(self, prefix: str, namespace: str):
    #====================================================
        if (pfx := self.__reverse_map.get(namespace)) is not None:
            self.__prefix_dict.pop(pfx, None)
        if (ns := self.__prefix_dict.get(prefix)) is not None:
            self.__reverse_map.pop(ns, None)
        self.__prefix_dict[prefix] = namespace
        self.__reverse_map[namespace] = prefix

    def curie(self, uri) -> str:
    #===========================
        for prefix, namespace in self.__prefix_dict.items():
            if uri.startswith(namespace):
                return f'{prefix}:{uri[len(namespace):]}'
        return uri

    def delete_prefix(self, prefix: str):
    #====================================
        if (ns := self.__prefix_dict.pop(prefix, None)) is not None:
            self.__reverse_map.pop(ns, None)

    def merge_namespaces(self, other: Self) -> Self:
    #===============================================
        for prefix, namespace in other.__prefix_dict.items():
            self.add_namespace(prefix, namespace)
        return self

    def simplify(self, term):
    #========================
        if isinstance(term, rdflib.URIRef):
            return self.curie(term)
        elif isinstance(term, rdflib.BNode):
            return str(term)
        elif isinstance(term, rdflib.Literal):
            if (dt := term.datatype) is not None:
                return f'"{str(term)}"^^{self.simplify(dt)}'
            return str(term)
        return term

#===============================================================================
