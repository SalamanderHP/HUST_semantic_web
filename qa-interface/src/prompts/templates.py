retrieval_qa_chat_prompt = """
Task: Generate a SPARQL SELECT statement for querying a graph database.
Instructions:
Use only the provided relationship types and properties in the
schema. Do not use any other relationship types or properties that
are not provided.

Remember the relationships are like Schema:
{schema}

Use REGEX for flexible text matching when searching device names, devices sensors, device networks.Make sure comparison is case-insensitive.

To retrieve both front and main cameras, use the hasCamera property along with cameraType filtering:
- Using ?smartphone onto:hasCamera ?frontCamera and ?frontCamera onto:cameraType "selfie_camera"
- Using ?smartphone onto:hasCamera ?mainCamera and ?mainCamera onto:cameraType "main_camera"
- You MUST use separate variables for the properties of frontCamera and mainCamera to avoid conflicts, e.g., ?frontCameraResolution and ?mainCameraResolution

When querying for RAM or storage specifications, do not use the name (?name) variable. Instead, apply your filter to the internalMemory property (?internalMemory), which is formatted as "RAM - Storage", e.g., "8GB - 128GB".

Note: The camera resolution property stores detailed camera specs as a text string, including resolution, aperture, focal length, and lens type (e.g., "48 MP, f/1.8, 26mm (wide); 13 MP, ...").
- Therefore, you CANNOT use numeric comparison operators (e.g., >, <) on camera resolution.  
- To filter for a minimum resolution (e.g., larger than 20MP), use REGEX or CONTAINS on the camera Resolution value instead,

Sensor names should be filtered based on English.

Also, for each URI object such as the operating system (os), CPU, battery, screen, and camera, include relevant descriptive properties by joining their details. Don’t just return the URI.

In the SELECT clause, you should ONLY include the name property (?name) of the smartphone.
All queries MUST include 'ORDER BY DESC(?releaseDate)' before the LIMIT clause to sort results by release date in descending order.
The query MUST include LIMIT 5 at the end to return at most 5 smartphone results.

Use PREFIX: 
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices/>

Example 1: Find all phones of a brand named "Apple"
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices/>
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
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices/>
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
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices/>
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
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices/>
SELECT DISTINCT ?name1 ?name2
WHERE {{
    ?smartphone1 onto:name ?name1 .
    ?smartphone2 onto:name ?name2 .
    
    FILTER(REGEX(?name1, "iPhone 16 Pro Max", "i"))
    FILTER(REGEX(?name2, "Galaxy S24 Ultra", "i"))
}}
LIMIT 1

Example 5: Find phones with excellent camera capabilities
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices/>
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

Example 6: I need a phone model under 5 million, with large battery capacity and good photography
PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices/>
SELECT DISTINCT ?name
WHERE {{
    ?smartphone onto:name ?name ;
                onto:price ?price ;
                onto:releaseDate ?releaseDate ;
                onto:hasBattery ?battery ;
                onto:hasCamera ?mainCamera .
    ?battery onto:capacity ?capacity .
    ?mainCamera onto:cameraType "main_camera" ;
                onto:cameraResolution ?mainCameraResolution .
    FILTER(?capacity >= 4000)  
    FILTER(?price < 5000000)  
    FILTER(REGEX(?mainCameraResolution, "48 MP|50 MP|64 MP|108 MP|200 MP", "i"))
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


response_prompt = """
    Giả sử bạn là một nhân viên tư vấn bán các sản phẩm điện thoại chuyên nghiệp, tôi sẽ cung cấp cho bạn câu hỏi của người dùng và một danh sách sản phẩm điện thoại thông minh.
    Bạn hãy trả lời câu hỏi của người dùng bằng cách sử dụng thông tin từ danh sách sản phẩm điện thoại thông minh mà tôi đã cung cấp cho bạn.
    Nếu người dùng có yêu cầu so sánh điện thoại, thì hãy so sánh tất cả các sản phẩm mà người dùng yêu cầu
    Còn nếu người dùng có nhu cầu mua máy thì hãy tư vấn cho họ khoảng 2 mẫu điện thoại dựa trên mô tả sản phẩm, hãy đưa ra ưu điểm của mỗi mẫu và giải thích vì sao nó phù hợp với người dùng.

    Danh sách sản phẩm điện thoại thông minh:
    {list_phone_prompt}

    Câu hỏi của người dùng: {user_question}
"""