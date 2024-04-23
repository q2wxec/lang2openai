import sys
import os
from patching import langchain_patch
langchain_patch.mk()

# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)

# 获取当前脚本的父目录的路径
current_dir = os.path.dirname(current_script_path)

# 获取父目录
parent_dir = os.path.dirname(current_dir)

# 获取根目录：
root_dir = os.path.dirname(parent_dir)

# 将项目根目录添加到sys.path
sys.path.append(root_dir)


from sanic import Sanic
from sanic import response as sanic_response

import os

from sanic.worker.manager import WorkerManager
import argparse

from api.embedding import embeddings
from api.rerank import rerank
from api.llm import chat,completions


WorkerManager.THRESHOLD = 6000
# 接收外部参数mode
parser = argparse.ArgumentParser()
# mode必须是local或online
parser.add_argument('--mode', type=str, default='local', help='local or online')
# 检查是否是local或online，不是则报错
args = parser.parse_args()
if args.mode not in ['local', 'online']:
    raise ValueError('mode must be local or online')

app = Sanic("Lang2OpenAI")
# 设置请求体最大为 10MB
app.config.REQUEST_MAX_SIZE = 400 * 1024 * 1024

# CORS中间件，用于在每个响应中添加必要的头信息
@app.middleware("response")
async def add_cors_headers(request, response):
    # response.headers["Access-Control-Allow-Origin"] = "http://10.234.10.144:5052"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"  # 如果需要的话

@app.middleware("request")
async def handle_options_request(request):
    if request.method == "OPTIONS":
        headers = {
            # "Access-Control-Allow-Origin": "http://10.234.10.144:5052",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true"  # 如果需要的话
        }
        return sanic_response.text("", headers=headers)

@app.before_server_start
async def init_modal(app, loop):
    from api.llm import get_llm_dict,get_chat_dict
    from api.rerank import get_rerank_dict
    from api.embedding import get_embeddings_dict
    app.ctx.embedding_models = get_embeddings_dict()
    app.ctx.reranke_models = get_rerank_dict()
    app.ctx.llm_models = get_llm_dict()
    app.ctx.chat_models = get_chat_dict()



app.add_route(embeddings, "/v1/embeddings", methods=['POST'])  # tags=["embeddings"] 
app.add_route(rerank, "/v1/rerank", methods=['POST'])  # tags=["rerank"] 
app.add_route(completions, "/v1/completions", methods=['POST'])  # tags=["completions"] 
app.add_route(chat, "/v1/chat/completions", methods=['POST'])  # tags=["chat"] 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8778, workers=4)
