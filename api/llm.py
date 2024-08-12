from sanic.response import json as sanic_json
from sanic.response import ResponseStream
from sanic import request
import json
import re

import asyncio
import os
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.llms.base import LLM
from langchain_core.messages import HumanMessage, SystemMessage,AIMessage
# from llm.adaptor.chat2llm import Chat2LLM
from utils.general_utils import *
from llm.llm_loader import getLLM,getChat,modal_type_dict
from modal.openai_api_modal import *
from direct.direct_request import pre_router

def get_function_prompt(question,functions)->str:
    BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))
    with open(BASE_DIR+'/prompt/function_call.prompt', 'r',encoding='utf-8') as f:
        function_prompt = f.read()
    # 替换function_prompt中的{question}和{functions}
    result = function_prompt.replace("{question}", question).replace("{functions}", functions)
    return result


async def chat(req: request):
    # models = req.app.ctx.chat_models
    model = safe_get(req, 'model')
    if not model in modal_type_dict:
        model = "glm-4"
    # glm接口与openai兼容，可以直接处理返回
    stream = safe_get(req, 'stream', False)
    messages = safe_get(req, 'messages', [])
    tools = safe_get(req, 'tools', [])
    temperature = safe_get(req, 'temperature', 0.01)
    functions = safe_get(req, 'functions', [])
    if functions and not tools:
        for function in functions:
            tool = {
                "type": "function",
                "function": function
            }
            tools.append(tool)
    resp = pre_router(req,'chat')
    if resp:
        return resp
    #print('messages:'+str(messages))
    #print('tools:'+str(tools))
    # spark-3.1最新消息必须来自用户
    if model == "spark-3.1" and messages[-1]['role'] != 'user' :
        messages[-1]['role'] = 'user'
    chat : BaseChatModel = getChat(model,temperature)
    chat_messages = []
    for message in messages:
        if message['content'] is None:
            message['content']=''
        if message['role'] == 'system':
            chat_message = SystemMessage(content=message['content'])
        elif message['role'] == 'user':
            chat_message = HumanMessage(content=message['content'])
        elif message['role'] == 'assistant':
            if message['tool_calls'] and len(message['tool_calls']) > 0:
                # tool_calls = []
                # for tool_call in message['tool_calls']:
                #     tc = ToolCall(name=tool_call['function']['name'],args=json.loads(tool_call['function']['arguments']),id = tool_call['id'])
                #     tool_calls.append(tc)
                # chat_message = AIMessage(content=message['content'],tool_calls=tool_calls)
                chat_message = AIMessage(content=message['content']+'/n工具调用情况如下：'+str(message['tool_calls']))
            else :  
                chat_message = AIMessage(content=message['content'])  
        elif message['role'] == 'tool':
            # chat_message = ToolMessage(content=message['content'],tool_call_id = message['tool_calls'])
            chat_message = AIMessage(content='工具调用结果如下，tool_call_id：'+message['tool_call_id']+' ,调用结果result:'+message['content'])
        chat_messages.append(chat_message)
    # tools不为空，说明是工具调用
    is_function_call = (tools and messages[-1]['role'] == 'user')
    if is_function_call:
        stream = False
        question = chat_messages.pop().content
        # 将tools转化为str
        functions = json.dumps(tools)
        function_prompt = get_function_prompt(question,functions)
        chat_message = HumanMessage(content=function_prompt)
        chat_messages.append(chat_message)
        
    prompt_tokens = sum(cal_tokens(s['content'], 'gpt-3.5-turbo') for s in messages)
    if stream:
        stream_resp = get_chat_stream_resp(model)
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
        resp = get_chat_resp(model)
        content = chat.invoke(chat_messages).content
        completion_tokens = cal_tokens(content, 'gpt-3.5-turbo')
        resp["usage"]["prompt_tokens"]= prompt_tokens
        resp["usage"]["completion_tokens"]= completion_tokens
        resp["usage"]["total_tokens"]= completion_tokens+prompt_tokens
        if is_function_call:
            tool_calls = []
            if is_valid_json_array(content):
                tool_array = json.loads(content)
            else:
                match = re.search(r'\[.*\]', content)
                if match:
                    tool_array = json.loads(match.group(0))
                else:
                    raise Exception('函数调用结果格式错误，请检查')
            for tool in tool_array:
                tool_resp = {
                        "id": uuid.uuid4().hex,
                        "type": "function",
                        "function": tool
                    }
                tool_calls.append(tool_resp)
            resp["choices"][0]['message']['tool_calls'] = tool_calls
        else:
            resp["choices"][0]['message']['content'] = content 
        #print('resp:'+str(resp))
        return sanic_json(resp)


async def completions(req: request):
    # models = req.app.ctx.llm_models
    resp = pre_router(req,'completions')
    if resp:
        return resp
    prompt = safe_get(req, 'prompt')
    stream = safe_get(req, 'stream', False)
    model = safe_get(req, 'model')
    temperature = safe_get(req, 'temperature', 0.01)
    llm : LLM = getLLM(model, temperature)
    prompt_tokens = cal_tokens(prompt, 'gpt-3.5-turbo')
    if stream:
        stream_resp = get_completions_stream_resp(model)
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
        resp = get_completions_resp(model)
        content = llm.invoke(prompt)
        resp["choices"][0]['text'] = content
        completion_tokens = cal_tokens(content, 'gpt-3.5-turbo')
        resp["usage"]["prompt_tokens"]= prompt_tokens
        resp["usage"]["completion_tokens"]= completion_tokens
        resp["usage"]["total_tokens"]= completion_tokens+prompt_tokens
        return sanic_json(resp)
    
    
