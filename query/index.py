from langchain.chains import GraphSparqlQAChain
from SPARQLWrapper import SPARQLWrapper, JSON
from langchain_community.graphs import RdfGraph
from langchain_openai import ChatOpenAI
from langchain_core.prompts.prompt import PromptTemplate
import os
from langchain.globals import set_debug
from dotenv import load_dotenv
from custom_rdf_graph import MyRdfGraph
from typing_extensions import Annotated, TypedDict
from langchain.chat_models import init_chat_model
from urllib.parse import urlencode
load_dotenv()

api_key = os.getenv("OPENAPI_KEY")

retrieval_qa_chat_prompt = """
Task: Generate a SPARQL SELECT statement for querying a graph database.
Instructions:
Use only the provided relationship types and properties in the
schema. Do not use any other relationship types or properties that
are not provided.

Remember the relationships are like Schema:
{schema}

Use CONTAINS or REGEX for flexible text matching when searching device names.Make sure the name comparison is case-insensitive.

To retrieve both front and main cameras, use the hasCamera property along with cameraType filtering:
- Using ?smartphone onto:hasCamera ?frontCamera and ?frontCamera onto:cameraType "selfie_camera"
- Using ?smartphone onto:hasCamera ?mainCamera and ?mainCamera onto:cameraType "main_camera"
- You MUST use separate variables for the properties of frontCamera and mainCamera to avoid conflicts, e.g., ?frontCameraResolution and ?mainCameraResolution

When querying for RAM or storage specifications, do not use the name (?name) variable. Instead, apply your filter to the internalMemory property (?internalMemory), which is formatted as "RAM - Storage", e.g., "8GB - 128GB".

Note: The camera resolution property stores detailed camera specs as a text string, including resolution, aperture, focal length, and lens type (e.g., "48 MP, f/1.8, 26mm (wide); 13 MP, ...").
- Therefore, you CANNOT use numeric comparison operators (e.g., >, <) on camera resolution.  
- To filter for a minimum resolution (e.g., larger than 20MP), use REGEX or CONTAINS on the camera Resolution value instead,

Also, for each URI object such as the operating system (os), CPU, battery, screen, and camera, include relevant descriptive properties by joining their details. Don’t just return the URI.

In the SELECT clause, you MUST include all data properties defined in the schema as separate variables. Do not skip any.
The query MUST include LIMIT 5 at the end to return at most 5 smartphone results.


Use PREFIX: 
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices#>
The question is:
{prompt}

Note: Be as concise as possible.
Do not include any explanations or apologies in your responses.
Do not respond to any questions that ask for anything else than for you to construct a SPARQL query.
Do not include any text except the SPARQL query generated.
When you make the final query, remove these ``` quotes and only have the query \n
"""
set_debug(True)
graph = MyRdfGraph(query_endpoint="http://localhost:3030/Semantic/sparql", standard="owl")
graph.load_schema()




class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]

# print(graph.get_schema)
sparql_select_prompt = PromptTemplate(
    input_variables=["schema", "question"], template=retrieval_qa_chat_prompt
)


prompt = sparql_select_prompt.invoke(
    {
        "schema": graph.get_schema,
        "prompt": "Tìm cho tôi điện thoại giá dưới 4 triệu và có hiệu năng cao",
    }
)

# print(prompt.text)

llm = init_chat_model("gpt-4o-mini", model_provider="openai", api_key=api_key, temperature=0)
structured_llm = llm.with_structured_output(QueryOutput)
result = structured_llm.invoke(prompt)

sparql = SPARQLWrapper("http://localhost:3030/Semantic/sparql")
sparql.setReturnFormat(JSON)
query = result["query"]
query = query.replace('\\n', '\n')

print(query)
sparql.setQuery(query)

try:
    ret = sparql.queryAndConvert()

    for r in ret["results"]["bindings"]:
        print(r)
except Exception as e:
    print(e)
# chain = GraphSparqlQAChain.from_llm(
#     ChatOpenAI(temperature=0, api_key=api_key, model="gpt-4o-mini"), 
#     graph=graph, 
#     verbose=True,
#     allow_dangerous_requests=True,
#     sparql_select_prompt=sparql_select_prompt,
# )




# chain.run("Thông tin điện thoại Samsung Galaxy S23 Ultra")