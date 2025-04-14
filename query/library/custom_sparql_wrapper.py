from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("http://localhost:3030/Semantic/sparql")
sparql.setReturnFormat(JSON)

def executeQuery(query: str):
    sparql.setQuery(query=query)
    try:
        ret = sparql.queryAndConvert()
        return ret["results"]["bindings"]
    except Exception as e:
        return []