import json
import csv
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD
import re
from datetime import datetime

SMP = Namespace("http://www.semanticweb.org/admin/ontologies/2025/2/smartdevices#")

def get_url(value):
    return re.sub(r'[^\w]', '_', value).lower()

def convert_csv(data: list[dict]):
    with open("smartphone.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["uri", "name"], quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writeheader()  # Ghi dòng tiêu đề
        writer.writerows(data)  # Ghi dữ liệu
# Load the JSON data from a file
with open('./phone_model.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

with open('./brand.json', 'r', encoding='utf-8') as f:
    brand_data = json.load(f)

g = Graph()
g.bind("smp", SMP)

uri_cache = {}

def get_or_create_shared_uri(prop_type, value):
    if not value:
        return None
    clean_value = get_url(value)
    uri_key = f"{prop_type}_{clean_value}"
    
    if uri_key not in uri_cache:
        uri_cache[uri_key] = SMP[clean_value]
    
    return uri_cache[uri_key]

result = []
for smartphone in json_data:
    product_name_clean = get_url(smartphone["device_name"])
    product_uri = SMP[product_name_clean]
    g.add((product_uri, RDF.type, SMP.SmartPhone))
    g.add((product_uri, SMP.name, Literal(smartphone["device_name"], datatype=XSD.string)))
    g.add((product_uri, SMP.sim, Literal(smartphone["sim"], datatype=XSD.int)))
    g.add((product_uri, SMP.weight, Literal(smartphone["body_weight"], datatype=XSD.float)))
    name = smartphone['device_name']
    result.append({"uri": product_uri, "name": name})
    # Brand
    if smartphone["brand"]:
        brand_name = smartphone["brand"]
        brand_name_key = brand_name.lower()
        if brand_name_key in brand_data:
            brand_uri = get_or_create_shared_uri("brand", brand_name)
            if brand_uri: 
                g.add((brand_uri, RDF.type, SMP.Brand))
                g.add((brand_uri, SMP.name, Literal(brand_name, datatype=XSD.string)))
                g.add((brand_uri, SMP.country, Literal(brand_data[brand_name_key]["country"], datatype=XSD.string)))
                if brand_data[brand_name_key]["foundDate"]:
                    g.add((brand_uri, SMP.foundedDate, Literal(brand_data[brand_name_key]["foundDate"], datatype=XSD.date)))
                g.add((product_uri, SMP.hasBrand, brand_uri))
    
    if smartphone["release_date"]:
        release_date = datetime.strptime(smartphone["release_date"], "%d/%m/%Y").strftime("%Y-%m-%d")
        g.add((product_uri, SMP.releaseDate, Literal(release_date, datatype=XSD.string)))
    
    if smartphone["network"]:
        networks = " / ".join(item for item in smartphone["network"])
        g.add((product_uri, SMP.networks, Literal(networks, datatype=XSD.string)))

    if smartphone["display"]:
        screen_uri = SMP[product_name_clean + "_screen"]
        g.add((product_uri, SMP.hasScreen, screen_uri))
        g.add((screen_uri, RDF.type, SMP.Screen))
        
        g.add((screen_uri, SMP.size, Literal(smartphone["display"]["size"], datatype=XSD.float)))
        g.add((screen_uri, SMP.brightness, Literal(smartphone["display"]["brightness"], datatype=XSD.int)))
        g.add((screen_uri, SMP.refreshRate, Literal(smartphone["display"]["refresh_rate"], datatype=XSD.int)))
        g.add((screen_uri, SMP.resolution, Literal(smartphone["display"]["resolution"], datatype=XSD.string)))
        g.add((screen_uri, SMP.type, Literal(smartphone["display"]["type"], datatype=XSD.string)))
    
    if smartphone["platform"]:
        # OS
        os_name = smartphone["platform"]["os"]
        os_uri = get_or_create_shared_uri("os", os_name)
        if os_uri:
            g.add((os_uri, RDF.type, SMP.OS))
            g.add((os_uri, SMP.name, Literal(os_name, datatype=XSD.string)))
            g.add((product_uri, SMP.hasOS, os_uri))

        # CPU
        chipset_name = smartphone["platform"]["chipset"]["name"]
        chipset_uri = get_or_create_shared_uri("cpu", chipset_name)
        if chipset_uri:
            g.add((chipset_uri, RDF.type, SMP.CPU))
            g.add((chipset_uri, SMP.name, Literal(chipset_name, datatype=XSD.string)))
            chipset_process = smartphone["platform"]["chipset"]["process"]
            if chipset_process:
                g.add((chipset_uri, SMP.process, Literal(chipset_process, datatype=XSD.string)))

            if smartphone["platform"]["cpu"]:
                core = smartphone["platform"]["cpu"]
                g.add((chipset_uri, SMP.core, Literal(core, datatype=XSD.string)))  

            # GPU
            gpu_name = smartphone["platform"]["gpu"]
            if gpu_name:
                g.add((chipset_uri, SMP.gpu, Literal(gpu_name, datatype=XSD.string)))
            
            g.add((product_uri, SMP.hasCPU, chipset_uri))
     
    # Chong nuoc
    if smartphone["waterproof"]:
        waterproof = smartphone["waterproof"]
        g.add((product_uri, SMP.waterproof, Literal(waterproof, datatype=XSD.string)))
    
    # Memory
    if smartphone["memory"]: 
        g.add((product_uri, SMP.cardSlot, Literal(smartphone["memory"]["card_slot"], datatype=XSD.boolean)))
        if smartphone["memory"]["internal"]:
            storages = ", ".join(f'{item["ram"]} - {item["storage"]}' for item in smartphone["memory"]["internal"])
            g.add((product_uri, SMP.internalMemory, Literal(storages, datatype=XSD.string)))
    
    # Camera
    for camera_type in ["selfie_camera", "main_camera"]:
        if camera_type == "selfie_camera":
            type = SMP.FrontCamera
        else:
            type = SMP.MainCamera

        if smartphone[camera_type]:
            camera_uri = SMP[product_name_clean + "_" + camera_type]
   
            g.add((camera_uri, RDF.type,  type))
            g.add((camera_uri, SMP.cameraType,  Literal(camera_type, datatype=XSD.string)))
            if smartphone[camera_type]["module"]:
                g.add((camera_uri, SMP.module, Literal(smartphone[camera_type]["module"], datatype=XSD.int)))

            if smartphone[camera_type]["features"]:
                features = ", ".join(item for item in smartphone[camera_type]["features"])
                g.add((camera_uri, SMP.features, Literal(features, datatype=XSD.string)))

            if smartphone[camera_type]["video"]:
                video = ", ".join(item for item in smartphone[camera_type]["video"])
                g.add((camera_uri, SMP.video, Literal(video, datatype=XSD.string)))
            
            if smartphone[camera_type]["resolution"] and len(smartphone[camera_type]["resolution"]) > 0:
                resolutions = ", ".join(item for item in smartphone[camera_type]["resolution"] if item)
                g.add((camera_uri, SMP.resolution, Literal(resolutions, datatype=XSD.string)))
            
            g.add((product_uri, SMP.hasCamera, camera_uri))

    # Sound
    if smartphone["sound"]: 
        g.add((product_uri, SMP.jack3_5, Literal(smartphone["sound"]["3.5mm_jack"], datatype=XSD.boolean)))
    
    # Comms
    if smartphone["comms"]: 
        g.add((product_uri, SMP.nfc, Literal(smartphone["comms"]["nfc"], datatype=XSD.boolean)))

    # Battery
    if smartphone["battery"]: 
        battery_uri = SMP[product_name_clean + "_battery"]
        g.add((battery_uri, RDF.type, SMP.Battery))
        g.add((battery_uri, SMP.capacity, Literal(smartphone["battery"]["capacity"], datatype=XSD.int)))
        g.add((battery_uri, SMP.batteryType, Literal(smartphone["battery"]["type"], datatype=XSD.string)))
        g.add((product_uri, SMP.hasBattery, battery_uri))

        # Charging
        if smartphone["battery"]["charging"]:
            for charger in smartphone["battery"]["charging"]:
                if charger["type"] in ["wired", "wireless"]:
                    charging_uri = SMP[product_name_clean + "_charging_" + charger["type"]]
                    if camera_type == "wired":
                        type = SMP.Wired
                    else:
                        type = SMP.Wireless
                    g.add((charging_uri, RDF.type, type))
                    g.add((charging_uri, SMP.chargerType, Literal(charger["type"], datatype=XSD.string)))
                    if charger["power"]:
                        power = charger["power"].replace("W", "")
                        g.add((charging_uri, SMP.power, Literal(float(power), datatype=XSD.float)))
                    g.add((product_uri, SMP.hasCharging, charging_uri))
    
    # Sensors
    if smartphone["features"]["sensors"]:
        if len(smartphone["features"]["sensors"]) > 0:
            sensors = ", ".join(item for item in smartphone["features"]["sensors"])
            g.add((product_uri, SMP.sensors, Literal(sensors, datatype=XSD.string)))

    # Colors
    if smartphone["colors"]:
        colors = ", ".join(item for item in smartphone["colors"])
        g.add((product_uri, SMP.colors, Literal(colors, datatype=XSD.string)))

    # Price
    if smartphone["price"]:
        g.add((product_uri, SMP.price, Literal(smartphone["price"], datatype=XSD.int)))

rdf_data = g.serialize(format='xml')
convert_csv(result)
with open("smartphone.data.rdf", "w") as f:
    f.write(rdf_data)

print("RDF data has been successfully generated and saved.")
