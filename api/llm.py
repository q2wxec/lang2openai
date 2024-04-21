from sanic.response import json as sanic_json
from sanic.response import ResponseStream
from sanic import request
import json
import time
import uuid
import asyncio
import os
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.llms.base import LLM
from langchain_core.messages import HumanMessage, SystemMessage,AIMessage

from utils.general_utils import *

def get_function_prompt(question,functions)->str:
    BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))
    with open(BASE_DIR+'/prompt/function_call.prompt', 'r',encoding='utf-8') as f:
        function_prompt = f.read()
    # 替换function_prompt中的{question}和{functions}
    result = function_prompt.replace("{question}", question).replace("{functions}", functions)
    return result

def get_llm_dict()->dict:
    from langchain_community.llms.tongyi import Tongyi
    from langchain_community.llms.baidu_qianfan_endpoint import QianfanLLMEndpoint
    from langchain_community.llms.sparkllm import SparkLLM
    return {
        "qwen-max": Tongyi(dashscope_api_key = get_config('llm','ty_api_key'),model_name='qwen-max'),
        "ERNIE-4.0":QianfanLLMEndpoint(qianfan_ak=get_config('llm','qf_ak'),qianfan_sk=get_config('llm','qf_sk'),model='ERNIE-4.0-8K'),
        "spark-3.1":SparkLLM(spark_app_id=get_config('llm','xh_app_id'),spark_api_key=get_config('llm','xh_api_key'),spark_api_secret=get_config('llm','xh_api_secret'),spark_llm_domain="generalv3",spark_api_url="ws://spark-api.xf-yun.com/v3.1/chat")
    }

def get_chat_dict()->dict:
    from langchain_community.chat_models import ChatTongyi
    from langchain_community.chat_models import QianfanChatEndpoint
    from langchain_community.chat_models import ChatSparkLLM
    return {
        "qwen-max": ChatTongyi(dashscope_api_key = get_config('llm','ty_api_key'),model_name='qwen-max'),
        "ERNIE-4.0":QianfanChatEndpoint(qianfan_ak=get_config('llm','qf_ak'),qianfan_sk=get_config('llm','qf_sk'),model='ERNIE-4.0-8K'),
        "spark-3.1":ChatSparkLLM(spark_app_id=get_config('llm','xh_app_id'),spark_api_key=get_config('llm','xh_api_key'),spark_api_secret=get_config('llm','xh_api_secret'),spark_llm_domain="generalv3",spark_api_url="ws://spark-api.xf-yun.com/v3.1/chat")
    }

async def chat(req: request):
    models = req.app.ctx.chat_models
    stream = safe_get(req, 'stream', False)
    model = safe_get(req, 'model')
    messages = safe_get(req, 'messages', [])
    tools = safe_get(req, 'tools', [])
    # tools不为空，说明是工具调用
    is_function_call = (tools != [])
    if model is None or model not in models:
        model = "qwen-max"
    chat : BaseChatModel = models[model]
    chat_messages = []
    for message in messages:
        if message['role'] == 'system':
            chat_message = SystemMessage(content=message['content'])
        elif message['role'] == 'user':
            chat_message = HumanMessage(content=message['content'])
        elif message['role'] == 'assistant':
            chat_message = AIMessage(content=message['content'])
        chat_messages.append(chat_message)
    if is_function_call:
        stream = False
        question = chat_messages.pop().content
        # 将tools转化为str
        functions = json.dumps(tools)
        function_prompt = get_function_prompt(question,functions)
        chat_message = HumanMessage(content=function_prompt)
        chat_messages.append(chat_message)
    resp = {
            "id": uuid.uuid4().hex,
            "object": "chat.completion",
            "created": time.time(),
            "model": model,
            "system_fingerprint": "",
            "choices": [{
                "index": 0,
                "message": {
                "role": "assistant",
                "content": "",
                "tool_calls":"",
                },
                "logprobs": '',
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    
    stream_resp = {
                    "id": uuid.uuid4().hex,
                    "object": "chat.completion.chunk",
                    "created": time.time(),
                    "model": model,
                    "system_fingerprint": "",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "role": "assistant",
                                "content": ""
                            },
                            "logprobs": '',
                            "finish_reason": ""
                        }
                    ],
                    "usage": {
                        "completion_tokens": 0,
                        "prompt_tokens": 0,
                        "total_tokens": 0
                    }
                }
    prompt_tokens = sum(cal_tokens(s['content'], 'gpt-3.5-turbo') for s in messages)
    if stream:
        async def generate_answer(response:ResponseStream):
            completion_tokens = 0
            for chunk in chat.stream(chat_messages):
                #logger.info(resp)
                resp_content = chunk.content
                completion_tokens += cal_tokens(resp_content, 'gpt-3.5-turbo')
                stream_resp["choices"][0]['delta']['content'] = resp_content
                await response.write(f"data: {json.dumps(stream_resp, ensure_ascii=False)}\n\n")
                # 确保流式输出不被压缩
                await asyncio.sleep(0.001)
            stream_resp["choices"][0]['finish_reason'] = "stop"
            stream_resp["usage"]["prompt_tokens"]= prompt_tokens
            stream_resp["usage"]["completion_tokens"]= completion_tokens
            stream_resp["usage"]["total_tokens"]= completion_tokens+prompt_tokens
            stream_resp["choices"][0]['delta'] = {}
            await response.write(f"data: {json.dumps(stream_resp, ensure_ascii=False)}\n\n")
                # 确保流式输出不被压缩
            await asyncio.sleep(0.001)
        return ResponseStream(generate_answer, content_type='text/event-stream')
    else:
        content = chat.invoke(chat_messages).content
        completion_tokens = cal_tokens(content, 'gpt-3.5-turbo')
        resp["usage"]["prompt_tokens"]= prompt_tokens
        resp["usage"]["completion_tokens"]= completion_tokens
        resp["usage"]["total_tokens"]= completion_tokens+prompt_tokens
        if is_function_call:
            resp["choices"][0]['message']['tool_calls'] = [
                    {
                        "id": uuid.uuid4().hex,
                        "type": "function",
                        "function": json.loads(content)
                    }
                ]
        else:
           resp["choices"][0]['message']['content'] = content 
        return sanic_json(resp)


async def completions(req: request):
    models = req.app.ctx.llm_models
    prompt = safe_get(req, 'prompt')
    stream = safe_get(req, 'stream', False)
    model = safe_get(req, 'model')
    if model is None or model not in models:
        model = "qwen-max"
    llm : LLM = models[model]
    resp = {
            "choices": [
                {
                "finish_reason": "length",
                "index": 0,
                "logprobs": '',
                "text": ""
                }
            ],
            "created": time.time(),
            "id": uuid.uuid4().hex,
            "model": model,
            "object": "text_completion",
            "usage": {
                "completion_tokens": 0,
                "prompt_tokens": 0,
                "total_tokens": 0
            }
        }
    stream_resp = {
            "choices": [
                {
                    "finish_reason": "",
                    "index": 0,
                    "logprobs": '',
                    "delta": {
                                "content": ""
                            },
                }
            ],
            "created":  time.time(),
            "id": uuid.uuid4().hex,
            "model": model,
            "object": "text_completion",
            "usage": {
                "completion_tokens": 0,
                "prompt_tokens": 0,
                "total_tokens": 0
            }
        }
    prompt_tokens = cal_tokens(prompt, 'gpt-3.5-turbo')
    if stream:
        async def generate_answer(response:ResponseStream):
            completion_tokens = 0
            for chunk in llm.stream(prompt):
                #logger.info(resp)
                resp_content = chunk
                completion_tokens += cal_tokens(resp_content, 'gpt-3.5-turbo')
                stream_resp["choices"][0]['delta']['content'] = resp_content
                await response.write(f"data: {json.dumps(stream_resp, ensure_ascii=False)}\n\n")
                # 确保流式输出不被压缩
                await asyncio.sleep(0.001)
            stream_resp["choices"][0]['finish_reason'] = "length"
            stream_resp["usage"]["prompt_tokens"]= prompt_tokens
            stream_resp["usage"]["completion_tokens"]= completion_tokens
            stream_resp["usage"]["total_tokens"]= completion_tokens+prompt_tokens
            stream_resp["choices"][0]['delta'] = {}
            await response.write(f"data: {json.dumps(stream_resp, ensure_ascii=False)}\n\n")
                # 确保流式输出不被压缩
            await asyncio.sleep(0.001)
        return ResponseStream(generate_answer, content_type='text/event-stream')
    else:
        content = llm.invoke(prompt)
        resp["choices"][0]['text'] = content
        completion_tokens = cal_tokens(content, 'gpt-3.5-turbo')
        resp["usage"]["prompt_tokens"]= prompt_tokens
        resp["usage"]["completion_tokens"]= completion_tokens
        resp["usage"]["total_tokens"]= completion_tokens+prompt_tokens
        return sanic_json(resp)