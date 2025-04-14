import json
import os
from openai import OpenAI
from openai.types.batch import Batch
from dotenv import load_dotenv
from pathlib import Path
import asyncio

script_dir = Path(__file__).resolve().parent
stop_flag = False

load_dotenv()
def create_batch_file_from_list_phone():
    try:
        phone_match_path = script_dir / "list_phone.json"
        with open(phone_match_path, 'r', encoding='utf-8') as f:
            phones = json.load(f)
        
        print(f"Đã tìm thấy {len(phones)} điện thoại trong file.")
        
        # Lấy template prompt từ openai_batch.py
        messages_template = [
            {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "Bạn là một chuyên gia về xử lý dữ liệu.Bạn có khả năng trích xuất và tổ chức thông tin ở dạng không có cấu trúc thành có cấu trú"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": "Hiện tại tôi đang cần trích xuất thông số kỹ thuật của các mẫu điện thoại.Tôi sẽ đưa cho bạn các dữ liệu về thông số kỹ thuật ở dạng bảng được hiển thị bằng thẻ table ở các trang web.Việc của bạn là trích xuất thông tin từ các bảng đó và trả kết quả cho tôi"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": "Ví dụ về đầu vào:\r\nName: Apple iPhone 16 Pro Max\r\nBrand: Apple\r\n<div> <p>Versions: A3296 (International); A3084 (USA); A3295 (Middle East, Canada, Mexico); A3297 (China, Hong Kong)</p> <table> <tr> <th>Network</th> <td><a>Technology</a></td> <td><a>GSM / CDMA / HSPA / EVDO / LTE / 5G</a></td> </tr> </table> <table> <tr> <th>Launch</th> <td><a>Announced</a></td> <td>2024, September 09</td> </tr> <tr> <td><a>Status</a></td> <td>Available. Released 2024, September 20</td> </tr> </table> <table> <tr> <th>Body</th> <td><a>Dimensions</a></td> <td>163 x 77.6 x 8.3 mm (6.42 x 3.06 x 0.33 in)</td> </tr><tr> <td><a>Weight</a></td> <td>227 g (8.01 oz)</td> </tr> <tr> <td><a>Build</a></td> <td>Glass front, glass back, titanium frame (grade 5)</td> </tr> <tr> <td><a>SIM</a></td> <td>Nano-SIM + <a>eSIM</a> + eSIM (max 2 at a time; International)<br/>eSIM + eSIM (8 or more, max 2 at a time; USA)<br/>Nano-SIM + Nano-SIM (China)</td> </tr> <tr><td> </td><td>IP68 dust tight and water resistant (immersible up to 6m for 30 min)<br> Apple Pay (Visa, MasterCard, AMEX certified)</br></td></tr> </table> <table> <tr> <th>Display</th> <td><a>Type</a></td> <td>LTPO Super Retina XDR OLED, 120Hz, HDR10, Dolby Vision, 1000 nits (typ), 2000 nits (HBM)</td> </tr> <tr> <td><a>Size</a></td> <td>6.9 inches, 115.6 cm<sup>2</sup> (~91.4% screen-to-body ratio)</td> </tr> <tr> <td><a>Resolution</a></td> <td>1320 x 2868 pixels, 19.5:9 ratio (~460 ppi density)</td> </tr> <tr> <td><a>Protection</a></td> <td>Ceramic Shield glass (2024 gen)</td> </tr> <tr><td> </td><td>Always-On display</td></tr> </table> <table> <tr> <th>Platform</th> <td><a>OS</a></td> <td>iOS 18, upgradable to iOS 18.3.2</td> </tr> <tr><td><a>Chipset</a></td> <td>Apple A18 Pro (3 nm)</td> </tr> <tr><td><a>CPU</a></td> <td>Hexa-core (2x4.05 GHz + 4x2.42 GHz)</td> </tr> <tr><td><a>GPU</a></td> <td>Apple GPU (6-core graphics)</td> </tr> </table> <table> <tr> <th>Memory</th> <td><a>Card slot</a></td> <td>No</td></tr> <tr> <td><a>Internal</a></td> <td>256GB 8GB RAM, 512GB 8GB RAM, 1TB 8GB RAM</td> </tr> <tr><td> </td><td>NVMe</td></tr> </table> <table> <tr> <th>Main Camera</th> <td><a>Triple</a></td> <td>48 MP, f/1.8, 24mm (wide), 1/1.28\", 1.22µm, dual pixel PDAF, sensor-shift OIS<br> 12 MP, f/2.8, 120mm (periscope telephoto), 1/3.06\", 1.12µm, dual pixel PDAF, 3D sensor‑shift OIS, 5x optical zoom<br> 48 MP, f/2.2, 13mm (ultrawide), 1/2.55\", 0.7µm, PDAF<br> TOF 3D LiDAR scanner (depth)</br></br></br></td> </tr> <tr> <td><a>Features</a></td> <td>Dual-LED dual-tone flash, HDR (photo/panorama)</td> </tr> <tr> <td><a>Video</a></td> <td>4K@24/25/30/60/100/120fps, 1080p@25/30/60/120/240fps, 10-bit HDR, Dolby Vision HDR (up to 60fps), ProRes, 3D (spatial) video/audio, stereo sound rec.</td> </tr> </table> <table> <tr> <th>Selfie camera</th> <td><a>Single</a></td> <td>12 MP, f/1.9, 23mm (wide), 1/3.6\", 1.0µm, PDAF, OIS<br> SL 3D, (depth/biometrics sensor)</br></td> </tr> <tr> <td><a>Features</a></td> <td>HDR, Dolby Vision HDR, 3D (spatial) audio, stereo sound rec.</td> </tr> <tr> <td><a>Video</a></td> <td>4K@24/25/30/60fps, 1080p@25/30/60/120fps, gyro-EIS</td> </tr> </table> <table> <tr> <th>Sound</th> <td><a>Loudspeaker</a> </td> <td>Yes, with stereo speakers</td> </tr> <tr> <td><a>3.5mm jack</a> </td> <td>No</td> </tr> </table> <table> <tr> <th>Comms</th> <td><a>WLAN</a></td> <td>Wi-Fi 802.11 a/b/g/n/ac/6e/7, tri-band, hotspot</td> </tr> <tr> <td><a>Bluetooth</a></td> <td>5.3, A2DP, LE</td> </tr> <tr> <td><a>Positioning</a></td> <td>GPS (L1+L5), GLONASS, GALILEO, BDS, QZSS, NavIC</td> </tr> <tr> <td><a>NFC</a></td> <td>Yes</td> </tr> <tr> <td><a>Radio</a></td> <td>No</td> </tr> <tr> <td><a>USB</a></td> <td>USB Type-C 3.2 Gen 2, DisplayPort</td> </tr> </table> <table> <tr> <th>Features</th> <td><a>Sensors</a></td> <td>Face ID, accelerometer, gyro, proximity, compass, barometer</td> </tr> <tr><td> </td><td>Ultra Wideband (UWB) support (gen2 chip)<br> Emergency SOS, Messages and Find My via satellite</br></td></tr> </table> <table> <tr> <th>Battery</th> <td><a>Type</a></td> <td>Li-Ion 4685 mAh</td> </tr> <tr> <td><a>Charging</a></td> <td>Wired, PD2.0, 50% in 30 min<br> 25W wireless (MagSafe), 15W wireless (China only)<br> 15W wireless (Qi2)<br> 4.5W reverse wired</br></br></br></td> </tr> </table> <table> <tr> <th>Misc</th> <td><a>Colors</a></td> <td>Black Titanium, White Titanium, Natural Titanium, Desert Titanium</td> </tr> <tr> <td><a>Models</a></td> <td>A3296, A3084, A3295, A3297, iPhone17,2</td> </tr> <tr> <td><a>SAR</a></td> <td>1.01 W/kg (head) 1.15 W/kg (body) </td> </tr> <tr> <td><a>SAR EU</a></td> <td>1.22 W/kg (head) 1.45 W/kg (body) </td> </tr> <tr> <td><a>Price</a></td> <td><a>$ 1,022.94 / € 1,253.99 / £ 1,080.00</a></td> </tr> </table> <table> <tr> <th>Tests</th> <td><a>Performance</a></td> <td> AnTuTu: 1838828 (v10)<br> GeekBench: 8606 (v6)<br/> 3DMark: 4731 (Wild Life Extreme)</br></td> </tr><tr> <td><a>Display</a></td> <td> <a>1796 nits max brightness (measured)</a></td> </tr><tr> <td><a>Loudspeaker</a></td> <td> <a>-24.4 LUFS (Very good)</a> </td> </tr><tr> <td><a>Battery (new)</a></td> <td> <div> <a>Active use score 17:18h</a><div></div> </div> </td> </tr><tr> </tr></table> </div>"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": "Bạn sẽ trả lời ở dạng json như sau: \r\n{\r\n    \"device_name\": \"Apple iPhone 16 Pro Max\",\r\n    \"brand\": \"Apple\",\r\n    \"release_date\": \"09/09/2024\",\r\n    \"network\": [\"gsm\",\"cdma\",\"hspa\",\"lte\",\"5g\"],\r\n    \"body_weight\": 227,\r\n    \"waterproof\": \"IP68\",\r\n    \"dimensions\": {\r\n        \"height\": 163,\r\n        \"width\": 77.6,\r\n        \"depth\": 8.3\r\n    },\r\n    \"sim\": 2,\r\n    \"display\": {\r\n        \"type\": \"OLED\",\r\n        \"refresh_rate\": 120,\r\n        \"size\": 6.9,\r\n        \"resolution\": \"1320 x 2868\",\r\n        \"ratio\": \"19.5:9\",\r\n        \"brightness\": 2000,\r\n        \"protection\": \"Ceramic Shield glass\",\r\n        \"feature\": [\"Always-On display\", \"HDR10\", \"Dolby Vision\"],\r\n        \"screen_to_body_ratio\": 91.4\r\n    },\r\n    \"platform\": {\r\n        \"os\": \"iOS 18\",\r\n        \"chipset\": {\r\n            \"name\": \"Apple A18 Pro\",\r\n            \"process\": \"3nm\"\r\n        },\r\n        \"cpu\": \"Hexa-core\",\r\n        \"gpu\": \"Apple GPU (6-core graphics)\"\r\n    },\r\n    \"memory\": {\r\n        \"card_slot\": false,\r\n        \"internal\": [\r\n            {\r\n                \"ram\": \"8GB\",\r\n                \"storage\": \"128GB\"\r\n            },\r\n            {\r\n                \"ram\": \"8GB\",\r\n                \"storage\": \"256GB\"\r\n            },\r\n            {\r\n                \"ram\": \"8GB\",\r\n                \"storage\": \"512GB\"\r\n            },\r\n            {\r\n                \"ram\": \"8GB\",\r\n                \"storage\": \"1TB\"\r\n            }\r\n        ]\r\n    },\r\n    \"main_camera\": {\r\n        \"module\": 3,\r\n        \"features\": [\"LiDAR scanner\", \"HDR\", \"Dual-LED dual-tone flash\"],\r\n        \"video\": [\"4K@24/25/30/60/100/120fps\", \"1080p@25/30/60/120/240fps\", \"10-bit HDR\", \"Dolby Vision HDR (up to 60fps)\", \"ProRes\", \"3D (spatial) video/audio\", \"stereo sound rec\"],\r\n        \"resolution\": [\"48 MP, f/1.8, 24mm (wide)\", \"12 MP, f/2.8, 120mm (periscope telephoto)\", \"48 MP, f/2.2, 13mm (ultrawide)\"]\r\n    },\r\n    \"selfie_camera\": {\r\n        \"module\": 1,\r\n        \"features\": [\"HDR\", \"Dolby Vision HDR\", \"3D (spatial) audio\", \"stereo sound rec\"],\r\n        \"video\": [\"4K@24/25/30/60fps\", \"1080p@25/30/60/120fps\", \"gyro-EIS\"],\r\n        \"resolution\": [\"12 MP, f/1.9, 23mm (wide)\"]\r\n    },\r\n    \"sound\": {\r\n        \"speaker\": \"stereo\",\r\n        \"3.5mm_jack\": false,\r\n        \"feature\": [\"Dolby Atmos\", \"Dolby Digital Plus\"]\r\n    },\r\n    \"comms\": {\r\n        \"wlan\": [\"Wi-Fi 802.11 a/b/g/n/ac/6e/7\", \"tri-band\", \"hotspot\"],\r\n        \"bluetooth\": \"5.3\",\r\n        \"nfc\": true,\r\n        \"radio\": false,\r\n        \"usb\": [\"USB Type-C 3.2 Gen 2\", \"DisplayPort\"]\r\n    },\r\n    \"battery\": {\r\n        \"type\": \"Li-Ion\",\r\n        \"capacity\": 4685,\r\n        \"charging\": [\r\n            {\r\n                \"type\": \"wired\",\r\n                \"power\": null\r\n            },\r\n            {\r\n                \"type\": \"wireless\",\r\n                \"power\": \"25W\"\r\n            },\r\n            {\r\n                \"type\": \"reverse wireless\",\r\n                \"power\": \"4.5W\"\r\n            }\r\n        ]\r\n    },\r\n    \"features\": {\r\n        \"sensors\": [\"Face ID\", \"accelerometer\", \"gyro\", \"proximity\", \"compass\", \"barometer\"],\r\n    },\r\n    \"colors\": [\"Black Titanium\", \"White Titanium\", \"Natural Titanium\", \"Desert Titanium\"]\r\n}"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": "Lưu ý đầu ra:\n- body_weight: chỉ lấy 1 giá trị, là khối lượng lớn nhất của dòng điện thoại đó\n- thuộc tính os trong platform: Chỉ lấy tên hệ điều hành.Ví dụ: Android 15, HyperOS 2\n- release_date: Định dạng dd/mm/yyyy\n- sim: Số lượng thẻ sim có thể hoạt động đồng thời\n- dimensions: chỉ lấy các thông số ở đơn vị mm\n- brightness: lấy độ sáng lớn nhất\n"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": "Việc của bạn là lấy thông tin từ bảng, nếu thông số nào không biết bạn hãy để giá trị là null, không được tự ý điền thông số kỹ thuật không chính xác"
                    }
                ]
            }
        ]
        
        # Tạo danh sách batch requests
        batch_requests = []
        list_id = []
        
        for i, phone in enumerate(phones):
            if 'html_specs' in phone and phone['html_specs']:
                # Tạo bản sao của template
                messages = []
                for message in messages_template:
                    message_copy = {
                        "role": message["role"],
                        "content": []
                    }
                    
                    for content in message["content"]:
                        content_copy = content.copy()
                        message_copy["content"].append(content_copy)
                    
                    messages.append(message_copy)
                
                # Thêm HTML specs như là nội dung cho user request
                html_message = {
                    "role": "user",
                    "content": [
                        {
                            "text": "Name: "+ phone["gsm"]["name"] + " \n Brand: " + phone["gsm"]["brand"] +" " +  phone['html_specs'],
                            "type": "text"
                        }
                    ]
                }
                messages.append(html_message)
                if phone["gsm"]["id"] not in list_id: 
                    list_id.append(phone["gsm"]["id"])
                    # Tạo một request trong batch
                    request = {
                        "custom_id": "{0}".format(phone["gsm"]["id"]),
                        "method": "POST",
                        "url": "/v1/chat/completions",
                        "body": {
                            "model": "gpt-4o-mini",
                            "messages": messages,
                            "max_tokens": 2048,
                            "temperature": 0.1,
                            "response_format": {"type": "json_object"}
                        }
                    }
                    batch_requests.append(request)
                else:
                    continue
                    
        # Lưu file batch
        batch_file_path = script_dir / "openai_batch_requests.jsonl"
        with open(batch_file_path, 'w', encoding='utf-8') as f:
            for request in batch_requests:
                f.write(json.dumps(request))
                f.write("\n")
                
        
        print(f"Đã tạo batch file với {len(batch_requests)} requests tại {batch_file_path}")
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")

def create_batch_request() -> Batch:
    api_key = os.getenv("OPENAPI_KEY")
    client = OpenAI(api_key=api_key)
    batch_input_file = client.files.create(
        file=open(script_dir / "openai_batch_requests.jsonl", "rb"),
        purpose="batch"
    )
    batch_input_file_id = batch_input_file.id
    batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "extract phone specs from gsmarena"
        }
    )

    return batch

async def get_batch_result(batch_id: str):
    api_key = os.getenv("OPENAPI_KEY")
    client = OpenAI(api_key=api_key)
    global stop_flag
    while not stop_flag:
        batch_status = client.batches.retrieve(batch_id)
        if(batch_status.errors != None):
            print(f"Batch {batch_id} has errors: {batch_status.errors}")
            stop_flag = True
            return
        if batch_status.status == "completed" and batch_status.output_file_id != None:
            file_response = client.files.content(batch_status.output_file_id)
            with open(script_dir / "batch_result.json", 'w', encoding='utf-8') as f:
                f.write(file_response.text)
            listSave = []
            listPhones = file_response.text.split("\n")
            for phone in listPhones:
                if not phone:
                    continue
                result = json.loads(phone)
                # print(result)
                phoneStr = result["response"]["body"]["choices"][0]["message"]["content"]
                phoneModel = json.loads(phoneStr)
                listSave.append(phoneModel)
            with open(script_dir / "final_result.json", 'w', encoding='utf-8') as f:
                f.write(json.dumps(listSave))

            merge_json_files()
            stop_flag = True
            print(f"Batch {batch_id} success.")
        
        if batch_status.status == "in_progress":
            print(f"Batch {batch_id} in_progress.")
        await asyncio.sleep(30)

# Ham này để merge thêm giá vào file final_result.json
# Giá của sản phẩm được lấy từ list_phone.json
def merge_json_files():
    # Mở final_result và list_phone
    with open(script_dir / 'final_result.json', 'r', encoding='utf-8') as f:
        final_result = json.load(f)
    
    with open(script_dir / 'list_phone.json', 'r', encoding='utf-8') as f:
        list_phone = json.load(f)

    for phone in final_result:
        for phone2 in list_phone:
            if phone["device_name"] == phone2["gsm"]["name"]:
                phone["price"] = phone2["price"]
                phone["description"] = phone2["description"]
                break
    # Mở file JSON đầu ra
    with open(script_dir / 'phone_model.json', 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)