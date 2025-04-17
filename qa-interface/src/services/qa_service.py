from langchain_core.prompts.prompt import PromptTemplate
import os
from langchain.globals import set_debug
from dotenv import load_dotenv
from src.library.custom_rdf_graph import MyRdfGraph
from src.utils.query_utils import executeQuery, query_devices_by_names, transform_phone_data
from typing_extensions import Annotated, TypedDict
from langchain.chat_models import init_chat_model
from src.prompts.templates import response_prompt, retrieval_qa_chat_prompt
from src.utils.format_utils import format_phone_to_prompt
from fastapi import WebSocket
import asyncio
load_dotenv()


class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]

class QAService:
    def __init__(self) -> None:
        set_debug(True)
        sparql_url = os.getenv("SPARQL_URL")
        api_key = os.getenv("OPENAPI_KEY")
        self.graph = MyRdfGraph(query_endpoint=sparql_url, standard="owl")
        self.graph.load_schema()
        self.sparql_llm = init_chat_model("gpt-4o-mini", model_provider="openai", api_key=api_key, temperature=0)
        self.response_llm = init_chat_model("gpt-4o-mini", model_provider="openai", api_key=api_key, temperature=0.5)

    async def question(self, question: str, socket: WebSocket):
        try:
            # Step 1: Generate SPARQL query
            sparql_select_prompt = PromptTemplate(
                input_variables=["schema", "question"], template=retrieval_qa_chat_prompt
            )

            prompt = sparql_select_prompt.invoke({
                "schema": self.graph.get_schema,
                "prompt": question,
            })
            structured_llm = self.sparql_llm.with_structured_output(QueryOutput)
            result = structured_llm.invoke(prompt)
            if "query" not in result:
                await socket.send_text("Lỗi hệ thống, vui lòng thử lại")
                return
            query = result["query"]
            query = query.replace('\\n', '\n')
            if len(query) == 0:
                await socket.send_text("Không thể tạo query truy vấn")
                return
            
            # Send the generated query immediately
            await socket.send_text(f"Generated Query:\n{query}")
            await asyncio.sleep(0)

            # Step 2: Execute SPARQL query
            ret = executeQuery(query=query)
            
            listDeviceName = []
         
            for r in ret:
                if "name" in r:
                    listDeviceName.append(r['name']['value'])
                else:
                    for key, _ in r.items():
                        if key.startswith('name'):
                            listDeviceName.append(r[key]['value'])
            
            if not listDeviceName:
                await socket.send_text(f"Query Results:\nFound 0 devices")
                await asyncio.sleep(0)
                return
            
            listPhones = query_devices_by_names(listDeviceName)
            result = transform_phone_data(listPhones)
            
            # Send the query results immediately
            await socket.send_text(f"Query Results:\nFound {len(listDeviceName)} devices: {', '.join(listDeviceName)}")
            await asyncio.sleep(0)

            # Step 3: Format phone data and generate response
            list_phone_prompt = ""
            for phone in result:
                list_phone_prompt += format_phone_to_prompt(phone) + "\n"
                list_phone_prompt += "-" * 50 + "\n"

            response_prompt_text = response_prompt.format(list_phone_prompt=list_phone_prompt, user_question=question)
            result = self.response_llm.invoke(response_prompt_text)
            
            # Send the final answer immediately
            await socket.send_text(f"Final Answer:\n{result.content}")

        except Exception as e:
            await socket.send_text(f"Error occurred: {str(e)}")
            



