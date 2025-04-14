from bs4 import BeautifulSoup
import requests
import json
import os
import time
import concurrent.futures
import random
from pathlib import Path

# Directory chứa script hiện tại
script_dir = Path(__file__).resolve().parent

# Định nghĩa headers để tránh bị chặn
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "Referer": "https://www.gsmarena.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

# Xử lý nội dung HTML
def process_html(content):
    soup = BeautifulSoup(content, 'html.parser')
    tables = soup.select_one("div#specs-list")
    
    if not tables:
        return None
    
    # Xóa các phần tử không cần thiết
    for tr in tables.find_all('tr', class_='tr-toggle'):
        tr.decompose()

    for tr in tables.find_all(['style']):
        tr.decompose()

    # Xóa tất cả các thuộc tính của thẻ
    for tag in tables.find_all(True):
        tag.attrs = {}
    
    # Chuyển thành một dòng HTML
    html_one_line = ' '.join(str(tables).split())
    return html_one_line

def create_gsm_url(brand_name, phone_id):
    """
    Tạo URL cho trang chi tiết điện thoại trên GSMArena
    
    Args:
        brand_name (str): Tên thương hiệu điện thoại
        phone_id (str): ID của điện thoại
        
    Returns:
        str: URL đã được tạo
    """
    # Chuyển đổi tên thương hiệu thành chữ thường
    url = brand_name.lower()
    
    # Thay thế khoảng trắng, dấu gạch ngang, gạch chéo và dấu chấm bằng dấu gạch dưới
    url = url.replace(' ', '_').replace('-', '_').replace('/', '_').replace('.', '_')
    
    # Thêm ID của điện thoại vào URL
    url = f"{url}-{phone_id}.php"
    
    return url
# Hàm xử lý một điện thoại và cập nhật JSON
def process_phone(phone_index, phone, all_phones):
    try:
        if 'gsm' not in phone or 'id' not in phone['gsm']:
            print(f"Điện thoại ở vị trí {phone_index} không có ID GSM")
            return False
            
        phone_id = phone['gsm']['id']
        phone_name1 = phone['gsm']['name']
        phone_name = phone.get('name', f"Phone ID: {phone_id}")
        url = f"https://www.gsmarena.com/{create_gsm_url(phone_name1, phone_id)}"
        
        print(f"Đang xử lý: {phone_name} (ID: {phone_id})")
        
        # Kiểm tra xem đã có html_specs chưa
        if 'html_specs' in phone and phone['html_specs']:
            print(f"Đã có dữ liệu HTML cho {phone_name}, bỏ qua.")
            return True
            
        # Tạo một delay ngẫu nhiên để tránh bị chặn
        time.sleep(random.uniform(5, 7))
        
        # Gửi request đến GSMArena
        response = requests.get(url, headers=headers, allow_redirects=True)
        
        if response.status_code == 200:
            # Xử lý HTML
            html_one_line = process_html(response.content)
            
            if html_one_line:
                # Cập nhật dữ liệu HTML vào đối tượng phone trong JSON
                all_phones[phone_index]['html_specs'] = html_one_line
                print(f"Đã cập nhật HTML cho: {phone_name}")
                return True
            else:
                print(f"Không tìm thấy bảng thông số cho: {phone_name}")
        else:
            print(f"Lỗi khi tải trang cho {phone_name}: {response.status_code}")
        
        return False
    
    except Exception as e:
        print(f"Lỗi xử lý {phone.get('name', 'unknown')}: {str(e)}")
        return False

# Lưu file JSON cập nhật sau mỗi batch nhất định
def save_json_file(phones, json_file_path, batch_id):
    try:
        # Tạo bản sao lưu
        backup_path = script_dir / f"gsm_cache/list_phone.backup_{batch_id}"
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(phones, f, ensure_ascii=False, indent=2)
        print(f"Đã sao lưu file JSON: {backup_path}")
        
        # Lưu file chính
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(phones, f, ensure_ascii=False, indent=2)
        print(f"Đã cập nhật file JSON: {json_file_path}")
        return True
    except Exception as e:
        print(f"Lỗi khi lưu file JSON: {str(e)}")
        return False

# Hàm chính
def excute():
    try:
        # Đọc file phone_match.json
        json_file_path = script_dir / "list_phone.json"
        
        with open(json_file_path, "r", encoding="utf-8") as f:
            phones = json.load(f)
 
        print(f"Đã tìm thấy {len(phones)} điện thoại trong file.")
        
        # Tạo danh sách các điện thoại cần xử lý
        phones_to_process = []
        for idx, phone in enumerate(phones):
            if 'html_specs' not in phone and 'gsm' in phone and 'id' in phone['gsm']:
                phones_to_process.append((idx, phone))
        
        print(f"Còn {len(phones_to_process)} điện thoại cần xử lý.")
        
        # Xử lý từng batch để có thể lưu định kỳ
        batch_size = 1
        current_batch = 0
        total_batches = (len(phones_to_process) + batch_size - 1) // batch_size
        
        for i in range(0, len(phones_to_process), batch_size):
            current_batch += 1
            batch = phones_to_process[i:i + batch_size]
            print(f"\nĐang xử lý batch {current_batch}/{total_batches} ({len(batch)} điện thoại)")
            
            # Xử lý đa luồng trong batch
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                futures = []
                for idx, phone in batch:
                    futures.append(executor.submit(process_phone, idx, phone, phones))
                
                # Đợi tất cả hoàn thành
                concurrent.futures.wait(futures)
            
            # Lưu sau mỗi batch
            save_json_file(phones, json_file_path, current_batch)
        print(f"\nHoàn thành tất cả các batch.")
    
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý: {str(e)}")