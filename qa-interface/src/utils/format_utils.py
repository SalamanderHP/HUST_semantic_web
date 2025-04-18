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

    if 'releaseDate' in phone_dict:
        prompt += f"Thời gian giới thiệu: {phone_dict['releaseDate']}\n"
    
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
    if "description" in phone_dict:
        prompt += f"Mô tả: {phone_dict['description']}\n"
    return prompt