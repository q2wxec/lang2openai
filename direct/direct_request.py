from utils.general_utils import *
from sanic import request
from sanic.response import json as sanic_json
from sanic.response import ResponseStream
import asyncio
import json

from llm.llm_loader import modal_type_dict
from modal.openai_api_modal import *

def pre_router(req: request,req_type:str = 'chat'):
    model = safe_get(req, 'model')
    if model :
        type = modal_type_dict[model]
        if type == 'tongyi':
            #return tongyi_chat(req)
            api_key =get_config('llm','ty_api_key')
            url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        elif type == 'zhipu':
            #return glm_chat(req)
            api_key =get_config('llm','zhipu_key')
            url = "https://open.bigmodel.cn/api/paas/v4"
        elif type == 'proxy':
            api_key = get_config('llm','proxy_key')
            url = get_config('llm','proxy_url')
        elif type == 'moonshot':
            api_key = get_config('llm','moonshot_key')
            url = "https://api.moonshot.cn/v1"
        elif type == 'spark':
            api_key = get_config('llm','xh_api_key')+':'+ get_config('llm','xh_api_secret')
            url = "https://spark-api-open.xf-yun.com/v1"
        return gpt_chat(req,url,api_key,req_type)
    return None


def gpt_chat(req: request,url:str,api_key:str,req_type:str):
    import httpx
    if req_type == 'chat':
        url = url+'/chat/completions'
    else:
        url = url+'/completions'
    params = req.json
    stream = safe_get(req, 'stream', False)

    # 请求数据
    data = params

    print('request:'+str(data))
    # 设置请求头部
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # 发送请求
    resp = httpx.post(url, json=data, headers=headers, timeout=120.0)
    if not stream:
        print('resp:'+str(resp))
        return sanic_json(resp.json())
    else:
        async def generate_answer(response:ResponseStream):
            for chunk in resp.iter_text():
                # 去除chunk开头的 data:
                if chunk.startswith("data:"):
                    chunk = chunk[5:]
                #logger.info(resp)
                await response.write(f"data: {chunk}\n\n")
                # 确保流式输出不被压缩
                await asyncio.sleep(0.001)
            # await response.write(f"data: {chunk}\n\n")
            #     # 确保流式输出不被压缩
            # await asyncio.sleep(0.001)
        return ResponseStream(generate_answer, content_type='text/event-stream')

# def glm_chat(req: request):
#     from zhipuai import ZhipuAI
#     stream = safe_get(req, 'stream', False)
#     model = safe_get(req, 'model')
#     messages = safe_get(req, 'messages', [])
#     tools = safe_get(req, 'tools', [])
#     tool_choice = safe_get(req, 'tool_choice', 'auto')
#     temperature = safe_get(req, 'temperature', 0)
#     client = ZhipuAI(api_key=get_config('llm','zhipu_key')) # 填写您自己的APIKey
#     req={
#         'model':model,  # 填写需要调用的模型名称
#         'messages':messages,
#         'stream':stream,
#         'temperature':temperature,
#     }
#     if tools:
#         req['tools'] = tools
#         req['tool_choice'] = tool_choice
#     #print(req)
#     resp = client.chat.completions.create(**req)
#     if not stream:
#         return sanic_json(json.loads(resp.model_dump_json(exclude_none = True)))
#     else:
#         async def generate_answer(response:ResponseStream):
#             for chunk in resp:
#                 #logger.info(resp)
#                 await response.write(f"data: {chunk.model_dump_json(exclude_none = True)}\n\n")
#                 # 确保流式输出不被压缩
#                 await asyncio.sleep(0.001)
#             # await response.write(f"data: {chunk.model_dump_json(exclude_none = True)}\n\n")
#             #     # 确保流式输出不被压缩
#             # await asyncio.sleep(0.001)
#         return ResponseStream(generate_answer, content_type='text/event-stream')
    

# def tongyi_chat(req: request):
#     from openai import OpenAI
#     stream = safe_get(req, 'stream', False)
#     model = safe_get(req, 'model')
#     messages = safe_get(req, 'messages', [])
#     for message in messages:
#         if not message['content']:
#             message['content']='工具调用'
#     tools = safe_get(req, 'tools', [])
#     tool_choice = safe_get(req, 'tool_choice', '')
#     temperature = safe_get(req, 'temperature', 0)
#     client = OpenAI(
#             api_key=get_config('llm','ty_api_key'),  # 替换成真实DashScope的API_KEY
#             base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务endpoint
#         )
#     req={
#         'model':model,  # 填写需要调用的模型名称
#         'messages':messages,
#         'stream':stream,
#         'temperature':temperature,
#         #'tool_choice':tool_choice,
#     }
#     if tools:
#         req['tools'] = tools
#     resp = client.chat.completions.create(**req)
#     if not stream:
#         return sanic_json(json.loads(resp.to_json(exclude_none = True)))
#     else:
#         async def generate_answer(response:ResponseStream):
#             for chunk in resp:
#                 #logger.info(resp)
#                 await response.write(f"data: {chunk.to_json(exclude_none = True, indent=None)}\n\n")
#                 # 确保流式输出不被压缩
#                 await asyncio.sleep(0.001)
#             # await response.write(f"data: {chunk.to_json(exclude_none = True, indent=None)}\n\n")
#             #     # 确保流式输出不被压缩
#             # await asyncio.sleep(0.001)
#         return ResponseStream(generate_answer, content_type='text/event-stream')