from langchain_openai import ChatOpenAI
from langchain_core.prompts.prompt import PromptTemplate
import os
from langchain.globals import set_debug
from dotenv import load_dotenv
from library.custom_rdf_graph import MyRdfGraph
from library.custom_sparql_wrapper import executeQuery
from typing_extensions import Annotated, TypedDict
from langchain.chat_models import init_chat_model
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

In the SELECT clause, you should ONLY include the name property (?name) of the smartphone.
All queries MUST include 'ORDER BY DESC(?releaseDate)' before the LIMIT clause to sort results by release date in descending order.
The query MUST include LIMIT 5 at the end to return at most 5 smartphone results.

Use PREFIX: 
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices#>

Example 1: Find all phones of a brand named "Apple"
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices#>
SELECT DISTINCT ?name
WHERE {{
    ?smartphone onto:name ?name ;
                onto:releaseDate ?releaseDate ;
                onto:hasBrand ?brand .
    ?brand onto:brandName "Apple" .
}}
ORDER BY DESC(?releaseDate)
LIMIT 5

Example 2: Find all phones with high-quality display
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices#>
SELECT DISTINCT ?name
WHERE {{
    ?smartphone onto:name ?name ;
                onto:releaseDate ?releaseDate ;
                onto:hasScreen ?screen .
    ?screen onto:type ?screenType ;
            onto:refreshRate ?refreshRate ;
            onto:brightness ?brightness .
    
    FILTER(REGEX(?screenType, "AMOLED|OLED", "i"))
    FILTER(?refreshRate >= 90)
    FILTER(?brightness >= 800)
}}
ORDER BY DESC(?releaseDate)
LIMIT 5

Example 3: Find phones based on multiple criteria (high-end devices)
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices#>
SELECT DISTINCT ?name
WHERE {{
    ?smartphone onto:name ?name ;
                onto:internalMemory ?internalMemory ;
                onto:hasCPU ?cpu ;
                onto:hasScreen ?screen ;
                onto:releaseDate ?releaseDate .
    
    ?cpu onto:cpuName ?cpuName .
    ?screen onto:refreshRate ?refreshRate .

    FILTER(REGEX(?cpuName, "Snapdragon 8|Dimensity 9000|A15|A16|A17|A18", "i"))
    FILTER(CONTAINS(?internalMemory, "8GB") || CONTAINS(?internalMemory, "12GB"))
    FILTER(?refreshRate >= 120)
}}
ORDER BY DESC(?releaseDate)
LIMIT 5

Example 4: Compare two phone models
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices#>
SELECT DISTINCT ?name1 ?name2
WHERE {{
    ?smartphone1 onto:name ?name1 .
    ?smartphone2 onto:name ?name2 .
    
    FILTER(REGEX(?name1, "iPhone 16 Pro Max", "i"))
    FILTER(REGEX(?name2, "Galaxy S24 Ultra", "i"))
}}
LIMIT 1

Example 5: Find phones with excellent camera capabilities
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices#>
SELECT DISTINCT ?name
WHERE {{
    ?smartphone onto:name ?name ;
                onto:releaseDate ?releaseDate ;
                onto:hasCamera ?mainCamera .
    
    ?mainCamera onto:cameraType "main_camera" ;
                onto:cameraResolution ?mainCameraResolution ;
                onto:features ?mainCameraFeatures ;
                onto:video ?mainCameraVideo .

    # Camera quality filters
    FILTER(REGEX(?mainCameraResolution, "48 MP|50 MP|64 MP|108 MP|200 MP", "i"))
    FILTER(REGEX(?mainCameraFeatures, "OIS|Night mode|HDR|Ultra Wide|Telephoto", "i"))
    FILTER(REGEX(?mainCameraVideo, "4K|8K", "i"))
}}
ORDER BY DESC(?releaseDate)
LIMIT 5

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
        "prompt": "Tôi cần tìm một mẫu điện thoại có dung lượng pin lớn, màn hình lớn và bộ nhớ lưu trữ lớn",
    }
)

def query_devices_by_names(listDeviceName):
    query = """PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices#>
    SELECT DISTINCT 
        ?name ?price ?internalMemory ?cardSlot ?colors ?networks 
        ?nfc ?jack3_5 ?sensors ?sim ?waterproof ?weight ?releaseDate

        # Brand properties
        ?brandName ?country ?foundedDate

        # CPU properties
        ?cpuName ?core ?process ?gpu

        # OS properties
        ?osName

        # Screen properties
        ?screenType ?size ?resolution ?refreshRate ?brightness

        # Battery properties
        ?batteryType ?capacity

        # Camera properties (Main)
        ?mainCameraResolution ?mainCameraType ?mainCameraFeatures 
        ?mainCameraModule ?mainCameraVideo

        # Camera properties (Front)
        ?frontCameraResolution ?frontCameraType ?frontCameraFeatures 
        ?frontCameraModule ?frontCameraVideo

        # Charger properties
        ?chargerType ?power

    WHERE {
        # Required properties
        ?smartphone onto:name ?name ;
            FILTER(?name IN (""" + ", ".join([f'"{name}"' for name in listDeviceName]) + """))
                

        # Group all basic smartphone properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:price ?price .
        }

        OPTIONAL { 
            ?smartphone onto:internalMemory ?internalMemory ;
                        onto:cardSlot ?cardSlot ;
                        onto:colors ?colors ;
                        onto:networks ?networks ;
                        onto:nfc ?nfc ;
                        onto:jack3_5 ?jack3_5 ;
                        onto:sensors ?sensors ;
                        onto:sim ?sim ;
                        onto:waterproof ?waterproof ;
                        onto:weight ?weight ;
                        onto:releaseDate ?releaseDate .
        }

        OPTIONAL {
            ?smartphone onto:hasBrand ?brand .
            ?brand  onto:brandName ?brandName ;
                    onto:country ?country ;
                    onto:foundedDate ?foundedDate .
        }

        # Group all CPU related properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:hasCPU ?cpu .
            ?cpu onto:cpuName ?cpuName ;
                onto:core ?core ;
                onto:process ?process ;
                onto:gpu ?gpu .
        }

        # Group all screen related properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:hasScreen ?screen .
            ?screen onto:type ?screenType ;
                    onto:size ?size ;
                    onto:resolution ?resolution ;
                    onto:refreshRate ?refreshRate ;
                    onto:brightness ?brightness .
        }

        # Group all battery related properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:hasBattery ?battery .
            ?battery onto:batteryType ?batteryType ;
                    onto:capacity ?capacity .
        }

        # Group all main camera properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:hasCamera ?mainCamera .
            ?mainCamera onto:cameraType "main_camera" ;
                        onto:cameraResolution ?mainCameraResolution ;
                        onto:features ?mainCameraFeatures ;
                        onto:module ?mainCameraModule ;
                        onto:video ?mainCameraVideo .
        }

        # Group all front camera properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:hasCamera ?frontCamera .
            ?frontCamera onto:cameraType "selfie_camera" ;
                        onto:cameraResolution ?frontCameraResolution ;
                        onto:features ?frontCameraFeatures ;
                        onto:module ?frontCameraModule ;
                        onto:video ?frontCameraVideo .
        }

        # Group all charger properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:hasCharger ?charger .
            ?charger onto:chargerType ?chargerType ;
                    onto:power ?power .
        }
    }
    LIMIT 5
    """
    return executeQuery(query=query)

# Sử dụng hàm


# llm = init_chat_model("gpt-4o-mini", model_provider="openai", api_key=api_key, temperature=0)
# structured_llm = llm.with_structured_output(QueryOutput)
# result = structured_llm.invoke(prompt)
result = {
  "query": "PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices#>\nSELECT DISTINCT ?name\nWHERE {\n    ?smartphone onto:name ?name ;\n                onto:releaseDate ?releaseDate ;\n                onto:hasBattery ?battery ;\n           onto:hasScreen ?screen ;\n                onto:internalMemory ?internalMemory .\n    ?battery onto:capacity ?batteryCapacity .\n    ?screen onto:size ?screenSize .\n\n    FILTER(?batteryCapacity >= 4000)  \n    FILTER(?screenSize >= 6.5)  \n    FILTER(CONTAINS(?internalMemory, \"128GB\") || CONTAINS(?internalMemory, \"256GB\") || CONTAINS(?internalMemory, \"512GB\"))\n}\nORDER BY DESC(?releaseDate)\nLIMIT 5"
}

query = result["query"]
query = query.replace('\\n', '\n')

def transform_phone_data(phones):
    transformed_phones = []
    
    for phone in phones:
        phone_obj = {}
        # Lặp qua từng thuộc tính của phone và lấy giá trị thực
        for key, value in phone.items():
            # Lấy giá trị từ trường 'value' của mỗi thuộc tính
            phone_obj[key] = value['value']
        
        transformed_phones.append(phone_obj)
    
    return transformed_phones

def convert_boolean_vi(value):
    if value.lower() == 'true':
        return 'Có'
    return 'Không'

def format_phone_to_prompt(phone_dict):
    prompt = f"""Mẫu điện thoại {phone_dict['name']}
"""
    # Thông tin cơ bản
    if 'price' in phone_dict:
        price = "{:,}".format(int(phone_dict['price'])) + " VNĐ"
        prompt += f"Giá bán: {price}\n"
    
    if 'internalMemory' in phone_dict:
        prompt += f"Bộ nhớ: {phone_dict['internalMemory']}\n"
    
    if 'cardSlot' in phone_dict:
        card_slot = convert_boolean_vi(phone_dict['cardSlot'])
        prompt += f"Thẻ nhớ: {card_slot} hỗ trợ\n"
    
    if 'colors' in phone_dict:
        prompt += f"Màu sắc: {phone_dict['colors']}\n"

    # Thông tin màn hình
    screen_info = []
    if 'screenType' in phone_dict:
        screen_info.append(f"Công nghệ {phone_dict['screenType']}")
    if 'size' in phone_dict:
        screen_info.append(f"{phone_dict['size']} inch")
    if 'resolution' in phone_dict:
        screen_info.append(f"độ phân giải {phone_dict['resolution']}")
    if 'refreshRate' in phone_dict:
        screen_info.append(f"tần số quét {phone_dict['refreshRate']}Hz")
    if 'brightness' in phone_dict:
        screen_info.append(f"độ sáng {phone_dict['brightness']} nits")
    if screen_info:
        prompt += f"Màn hình: {', '.join(screen_info)}\n"

    # Thông tin vi xử lý
    cpu_info = []
    if 'cpuName' in phone_dict:
        cpu_info.append(phone_dict['cpuName'])
    if 'core' in phone_dict:
        cpu_info.append(phone_dict['core'])
    if 'process' in phone_dict:
        cpu_info.append(f"tiến trình {phone_dict['process']}")
    if cpu_info:
        prompt += f"Vi xử lý: {', '.join(cpu_info)}\n"
    if 'gpu' in phone_dict:
        prompt += f"GPU: {phone_dict['gpu']}\n"

    # Camera
    if 'mainCameraResolution' in phone_dict:
        prompt += f"Camera chính: {phone_dict['mainCameraResolution']}\n"
        if 'mainCameraFeatures' in phone_dict:
            prompt += f"Tính năng camera: {phone_dict['mainCameraFeatures']}\n"
        if 'mainCameraVideo' in phone_dict:
            prompt += f"Quay video: {phone_dict['mainCameraVideo']}\n"

    if 'frontCameraResolution' in phone_dict:
        prompt += f"Camera selfie: {phone_dict['frontCameraResolution']}\n"

    # Pin và sạc
    battery_info = []
    if 'batteryType' in phone_dict and phone_dict['batteryType'] != 'None':
        battery_info.append(phone_dict['batteryType'])
    if 'capacity' in phone_dict:
        battery_info.append(f"{phone_dict['capacity']}mAh")
    if battery_info:
        prompt += f"Pin: {', '.join(battery_info)}\n"
    if 'chargerType' in phone_dict and 'power' in phone_dict:
        prompt += f"Sạc: {phone_dict['chargerType']}, công suất {phone_dict['power']}W\n"

    # Các tính năng khác
    features = []
    if 'networks' in phone_dict:
        features.append(f"Mạng: {phone_dict['networks']}")
    if 'nfc' in phone_dict:
        nfc = convert_boolean_vi(phone_dict['nfc'])
        features.append(f"NFC: {nfc}")
    if 'jack3_5' in phone_dict:
        jack = convert_boolean_vi(phone_dict['jack3_5'])
        features.append(f"Jack 3.5mm: {jack}")
    if 'waterproof' in phone_dict:
        features.append(f"Chống nước: {phone_dict['waterproof']}")
    if 'sensors' in phone_dict:
        features.append(f"Cảm biến: {phone_dict['sensors']}")
    if features:
        prompt += "Tính năng khác: \n"
        if 'networks' in phone_dict:
            prompt += f"- Mạng: {phone_dict['networks']}\n"
        if 'nfc' in phone_dict:
            nfc = convert_boolean_vi(phone_dict['nfc'])
            prompt += f"- NFC: {nfc}\n"
        if 'jack3_5' in phone_dict:
            jack = convert_boolean_vi(phone_dict['jack3_5'])
            prompt += f"- Jack 3.5mm: {jack}\n"
        if 'waterproof' in phone_dict:
            prompt += f"- Chống nước: {phone_dict['waterproof']}\n"
        if 'sensors' in phone_dict:
            prompt += f"- Cảm biến: {phone_dict['sensors']}\n"

    return prompt
try:
    ret = executeQuery(query=query)
    listDeviceName = [r['name']['value'] for r in ret]
    listPhones = query_devices_by_names(listDeviceName)
    result = transform_phone_data(listPhones)
    for phone in result:
        print(format_phone_to_prompt(phone))
        print("-" * 50)
    # print(result)
except Exception as e:
    print(e)




