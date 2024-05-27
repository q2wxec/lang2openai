from utils.general_utils import *
from sanic import request
from sanic.response import json as sanic_json
from sanic.response import ResponseStream
import asyncio
import json

from llm.llm_loader import modal_type_dict
from modal.openai_api_modal import *

def pre_router(req: request):
    model = safe_get(req, 'model')
    if model :
        type = modal_type_dict[model]
        if type == 'tongyi':
            return tongyi_chat(req)
        elif type == 'zhipu':
            return glm_chat(req)
    return None

def glm_chat(req: request):
    from zhipuai import ZhipuAI
    stream = safe_get(req, 'stream', False)
    model = safe_get(req, 'model')
    messages = safe_get(req, 'messages', [])
    tools = safe_get(req, 'tools', [])
    functions = safe_get(req, 'functions', [])
    if functions and not tools:
        for function in functions:
            tool = {
                "type": "function",
                "function": function
            }
            tools.append(tool)
    tool_choice = safe_get(req, 'tool_choice', 'auto')
    temperature = safe_get(req, 'temperature', 0)
    client = ZhipuAI(api_key=get_config('llm','zhipu_key')) # 填写您自己的APIKey
    req={
        'model':model,  # 填写需要调用的模型名称
        'messages':messages,
        'stream':stream,
        'temperature':temperature,
    }
    if tools:
        req['tools'] = tools
        req['tool_choice'] = tool_choice
    print(req)
    resp = client.chat.completions.create(**req)
    if not stream:
        return sanic_json(json.loads(resp.model_dump_json(exclude_none = True)))
    else:
        async def generate_answer(response:ResponseStream):
            for chunk in resp:
                #logger.info(resp)
                await response.write(f"data: {chunk.model_dump_json(exclude_none = True)}\n\n")
                # 确保流式输出不被压缩
                await asyncio.sleep(0.001)
            await response.write(f"data: {chunk.model_dump_json(exclude_none = True)}\n\n")
                # 确保流式输出不被压缩
            await asyncio.sleep(0.001)
        return ResponseStream(generate_answer, content_type='text/event-stream')
    
# def tongyi_chat(req: request):
#     from dashscope import Generation
#     stream = safe_get(req, 'stream', False)
#     model = safe_get(req, 'model')
#     messages = safe_get(req, 'messages', [])
#     tools = safe_get(req, 'tools', [])
#     temperature = safe_get(req, 'temperature', 0)
#     for message in messages:
#         if not message['content']:
#             message['content']='工具调用'
#     client = Generation
#     req={
#         'api_key':get_config('llm','ty_api_key'),
#         'model':model,  # 填写需要调用的模型名称
#         'messages':messages,
#         'stream':stream,
#         'result_format':'message',  # 将输出设置为message形式
#         'temperature':temperature,
#     }
#     if stream:
#         req['incremental_output'] = True
#     if tools:
#         req['tools'] = tools
#     resp = client.call(**req)
#     if not stream:
#         #print(resp)
#         openai_resp = get_chat_resp(model)
#         openai_resp['choices'] = resp['output']['choices']
#         openai_resp['choices'][0]['index'] = 0
#         openai_resp["usage"]["prompt_tokens"]= resp['usage']['input_tokens']
#         openai_resp["usage"]["completion_tokens"]= resp['usage']['output_tokens']
#         openai_resp["usage"]["total_tokens"]= resp['usage']['total_tokens']
#         return sanic_json(openai_resp)
#     else:
#         openai_resp = get_chat_stream_resp(model)
#         async def generate_answer(response:ResponseStream):
#             for chunk in resp:
#                 openai_resp["choices"][0]['delta']['content'] = chunk['output']['choices'][0]['message']['content']
#                 openai_resp["choices"][0]['finish_reason'] = chunk['output']['choices'][0]['finish_reason']
#                 openai_resp["choices"][0]['index'] = 0
#                 openai_resp["usage"]["prompt_tokens"]= chunk['usage']['input_tokens']
#                 openai_resp["usage"]["completion_tokens"]= chunk['usage']['output_tokens']
#                 openai_resp["usage"]["total_tokens"]= chunk['usage']['total_tokens']
#                 #logger.info(resp)
#                 await response.write(f"data: {json.dumps(openai_resp)}\n\n")
#                 # 确保流式输出不被压缩
#                 await asyncio.sleep(0.001)
#             await response.write(f"data: {json.dumps(openai_resp)}\n\n")
#                 # 确保流式输出不被压缩
#             await asyncio.sleep(0.001)
#         return ResponseStream(generate_answer, content_type='text/event-stream')
def tongyi_chat(req: request):
    from openai import OpenAI
    stream = safe_get(req, 'stream', False)
    model = safe_get(req, 'model')
    messages = safe_get(req, 'messages', [])
    for message in messages:
        if not message['content']:
            message['content']='工具调用'
    tools = safe_get(req, 'tools', [])
    tool_choice = safe_get(req, 'tool_choice', '')
    temperature = safe_get(req, 'temperature', 0)
    client = OpenAI(
            api_key=get_config('llm','ty_api_key'),  # 替换成真实DashScope的API_KEY
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务endpoint
        )
    req={
        'model':model,  # 填写需要调用的模型名称
        'messages':messages,
        'stream':stream,
        'temperature':temperature,
        #'tool_choice':tool_choice,
    }
    if tools:
        req['tools'] = tools
    resp = client.chat.completions.create(**req)
    if not stream:
        return sanic_json(json.loads(resp.to_json(exclude_none = True)))
    else:
        async def generate_answer(response:ResponseStream):
            for chunk in resp:
                #logger.info(resp)
                await response.write(f"data: {chunk.to_json(exclude_none = True, indent=None)}\n\n")
                # 确保流式输出不被压缩
                await asyncio.sleep(0.001)
            await response.write(f"data: {chunk.to_json(exclude_none = True, indent=None)}\n\n")
                # 确保流式输出不被压缩
            await asyncio.sleep(0.001)
        return ResponseStream(generate_answer, content_type='text/event-stream')