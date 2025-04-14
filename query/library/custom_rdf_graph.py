from langchain_community.graphs import RdfGraph
import langchain_community.graphs.rdf_graph as rdf

# Object Properties with domain and range
op_query_full = (
    rdf.prefixes["rdfs"]
    + rdf.prefixes["owl"]
    + (
        """SELECT DISTINCT ?op ?domain ?range ?com\n"""
        """WHERE {\n"""
        """  ?op a/rdfs:subPropertyOf* owl:ObjectProperty .\n"""
        """  OPTIONAL { ?op rdfs:domain ?domain . }\n"""
        """  OPTIONAL { ?op rdfs:range ?range . }\n"""
        """  OPTIONAL { ?op rdfs:comment ?com . }\n"""
        """}"""
    )
)

# Datatype Properties with domain and range
dp_query_full = (
    rdf.prefixes["rdfs"]
    + rdf.prefixes["owl"]
    + (
        """SELECT DISTINCT ?dp ?domain ?range ?com\n"""
        """WHERE {\n"""
        """  ?dp a/rdfs:subPropertyOf* owl:DatatypeProperty .\n"""
        """  OPTIONAL { ?dp rdfs:domain ?domain . }\n"""
        """  OPTIONAL { ?dp rdfs:range ?range . }\n"""
        """  OPTIONAL { ?dp rdfs:comment ?com . }\n"""
        """}"""
    )
)

class MyRdfGraph(RdfGraph):
    def load_schema(self) -> None:
        """
        Load and present the graph schema with explicit domain and range for relationships.
        """

        def _res_to_str_with_domain_range(r, prop_type="op"):
            """
            Helper to format properties with optional comments, domain and range.
            Strips full URI and prints each entry on its own line.
            """
            uri = str(r.get(prop_type))
            comment = str(r.get("com", "")).strip()
            domain = str(r.get("domain", "🟥 unknown"))
            range_ = str(r.get("range", "🟥 unknown"))

            # Lấy local name từ URI
            local_name = uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]
            domain_name = domain.split("#")[-1] if "#" in domain else domain.split("/")[-1]
            range_name = range_.split("#")[-1] if "#" in range_ else range_.split("/")[-1]

            description = f" ({comment})" if comment else ""
            return f"{local_name}: {domain_name} → {range_name}{description}"
        
        def _res_to_str_cls_filtered(r):
            uri = str(r.get("cls"))
            if "semanticweb.org" in uri:
                local_name = uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]
                return local_name
            return None
        
        def _res_to_str_data_property(r):
            uri = str(r.get("dp"))
            comment = str(r.get("com", "")).strip() or "(none)"
            domain = str(r.get("domain", "🟥 unknown"))
            range_ = str(r.get("range", "🟥 unknown"))

            prop_name = uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]
            domain_name = domain.split("#")[-1] if "#" in domain else domain.split("/")[-1]
            range_name = range_.split("#")[-1] if "#" in range_ else range_.split("/")[-1]

            return f"{prop_name}: belongs to {domain_name}, type xsd:{range_name}, note: {comment}"

        if self.standard == "rdf":
            clss = self.query(rdf.cls_query_rdf)
            rels = self.query(rdf.rel_query_rdf)
            self.schema = rdf._rdf_s_schema(clss, rels)

        elif self.standard == "rdfs":
            clss = self.query(rdf.cls_query_rdfs)
            rels = self.query(rdf.rel_query_rdfs)
            self.schema = rdf._rdf_s_schema(clss, rels)

        elif self.standard == "owl":
            clss = self.query(rdf.cls_query_owl)
             # Lọc class bạn định nghĩa
            custom_classes = filter(None, (_res_to_str_cls_filtered(r) for r in clss))

            # Query object properties with domain and range
            ops = self.query(op_query_full)

            # Query datatype properties with domain and range
            dps = self.query(dp_query_full)

            self.schema = (
                f"In the following, each property is followed by its domain → range "
                f"and optionally its description.\n\n"
                f"Use only the following classes that are defined by the ontology author:\n"
                f"{chr(10).join(sorted(custom_classes))}\n\n"
                f"Object Properties (relationships between objects):\n"
                f"{chr(10).join([_res_to_str_with_domain_range(r, 'op') for r in ops])}\n\n"
                f"Data Properties (attributes with literal values):\n"
                f"{chr(10).join([_res_to_str_data_property(r) for r in dps])}\n"
            )

        else:
            raise ValueError(f"Mode '{self.standard}' is currently not supported.")

  