import asyncio
from typing import Any
from fastapi import FastAPI
import json
import extract_data.crawl_data as CrawlData
import extract_data.create_batch_process as CreateBatchProcess
from openai.types.batch import Batch

app = FastAPI()

async def crawl_html():
    print(f"Start crawling data for")
    CrawlData.excute()

    print("Start create openAI batch file")
    CreateBatchProcess.create_batch_file_from_list_phone()

    print("Start create openAI batch request")
    batch_info = CreateBatchProcess.create_batch_request()

    print("Get response")
    await CreateBatchProcess.get_batch_result(batch_info.id)
    print(f"Done with")

@app.post("/crawl_data/")
async def crawl_data(request: list[dict[str, Any]]):
    # Lưu list phone vào file
    with open("crawl_data/extract_data/list_phone.json", "w", encoding="utf-8") as f:
        json.dump(request, f, ensure_ascii=False, indent=2)
        asyncio.create_task(crawl_html())
    return {"message": "Đã bắt đầu xử lý trong thread!"}