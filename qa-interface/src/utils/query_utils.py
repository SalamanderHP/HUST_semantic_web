from dotenv import load_dotenv
from SPARQLWrapper import SPARQLWrapper, JSON
import os
load_dotenv()
sparql_url = os.getenv("SPARQL_URL")
sparql = SPARQLWrapper(sparql_url)
sparql.setReturnFormat(JSON)

def executeQuery(query: str):
    sparql.setQuery(query=query)
    try:
        ret = sparql.queryAndConvert()
        return ret["results"]["bindings"]
    except Exception as e:
        return []
    
def query_devices_by_names(listDeviceName):
    query = """PREFIX onto:<http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices/>
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
        ?mainCameraResolution ?mainCameraFeatures 
        ?mainCameraModule ?mainCameraVideo

        # Camera properties (Front)
        ?frontCameraResolution ?frontCameraFeatures 
        ?frontCameraModule ?frontCameraVideo

        # Charger properties
        ?chargerType ?power
        ?description

    WHERE {
        # Required properties
        ?smartphone onto:name ?name ;
            FILTER(?name IN (""" + ", ".join([f'"{name}"' for name in listDeviceName]) + """))
        
        # Group all basic smartphone properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:price ?price .
        }

        OPTIONAL {
            ?smartphone onto:description ?description .
        }

        OPTIONAL { 
    		OPTIONAL { ?smartphone onto:internalMemory ?internalMemory  }
    		OPTIONAL { ?smartphone onto:cardSlot ?cardSlot  }
    		OPTIONAL { ?smartphone onto:colors ?colors  }
    		OPTIONAL { ?smartphone onto:networks ?networks  }
    		OPTIONAL { ?smartphone onto:nfc ?nfc  }
    		OPTIONAL { ?smartphone onto:jack3_5 ?jack3_5  }
    		OPTIONAL { ?smartphone onto:sensors ?sensors  }
    		OPTIONAL { ?smartphone onto:sim ?sim  }
    		OPTIONAL { ?smartphone onto:waterproof ?waterproof  }
    		OPTIONAL { ?smartphone onto:weight ?weight  }
    		OPTIONAL { ?smartphone onto:releaseDate ?releaseDate  }
        }

        OPTIONAL {
            ?smartphone onto:hasBrand ?brand .
            ?brand  onto:brandName ?brandName ;
                    onto:country ?country ;
                    onto:foundedDate ?foundedDate .
        }

        OPTIONAL {
            ?smartphone onto:hasOS ?os .
            ?os  onto:osName ?osName .
        }

        # Group all CPU related properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:hasCPU ?cpu .
            ?cpu onto:cpuName ?cpuName .
            OPTIONAL { ?cpu onto:core ?core }
            OPTIONAL { ?cpu onto:process ?process }
            OPTIONAL { ?cpu onto:gpu ?gpu }
        }

        # Group all screen related properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:hasScreen ?screen .
            OPTIONAL { ?screen onto:type ?screenType  }
            OPTIONAL { ?screen onto:size ?size  }
            OPTIONAL { ?screen onto:resolution ?resolution  }
            OPTIONAL { ?screen onto:refreshRate ?refreshRate  }
            OPTIONAL { ?screen onto:brightness ?brightness  }
        }

        # Group all battery related properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:hasBattery ?battery .
            OPTIONAL { ?battery onto:batteryType ?batteryType  }
            OPTIONAL { ?battery onto:capacity ?capacity  }
        }

        # Group all main camera properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:hasCamera ?mainCamera .
            ?mainCamera onto:cameraType "main_camera" .
            OPTIONAL { ?mainCamera onto:cameraResolution ?mainCameraResolution  }
            OPTIONAL { ?mainCamera onto:features ?mainCameraFeatures  }
            OPTIONAL { ?mainCamera onto:module ?mainCameraModule  }
            OPTIONAL { ?mainCamera onto:video ?mainCameraVideo  }
        }

        # Group all front camera properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:hasCamera ?frontCamera .
            ?frontCamera onto:cameraType "selfie_camera" .
            OPTIONAL { ?frontCamera onto:cameraResolution ?frontCameraResolution  }
            OPTIONAL { ?frontCamera onto:features ?frontCameraFeatures  }
            OPTIONAL { ?frontCamera onto:module ?frontCameraModule  }
            OPTIONAL { ?frontCamera onto:video ?frontCameraVideo  }
        }

        # Group all charger properties in one OPTIONAL
        OPTIONAL {
            ?smartphone onto:hasCharger ?charger .
            ?charger onto:chargerType ?chargerType ;
                    onto:power ?power .
        }
    }
    ORDER BY DESC(?price)
    LIMIT 5
    """
    return executeQuery(query=query)


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
