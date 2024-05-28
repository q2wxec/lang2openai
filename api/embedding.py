from sanic.response import json as sanic_json
from sanic import request
import os


from utils.general_utils import *

def get_embeddings_dict()->dict:
    from langchain.embeddings.huggingface import HuggingFaceEmbeddings
    result = {}
    # if get_config('embedding','bge_embedding_path'):
    #     result["bge-large-zh-v1.5"] = HuggingFaceBgeEmbeddings(model_name=get_config('embedding','bge_embedding_path'))
    if get_config('embedding','embedding_path'):
        embedding_pathes = get_config('embedding','embedding_path')
        embedding_path_list = embedding_pathes.split(',')
        for embedding_path in embedding_path_list:
            model = os.path.basename(embedding_path)
            result[model] = HuggingFaceEmbeddings(model_name=embedding_path)
    return result
async def embeddings(req: request):
    models = req.app.ctx.embedding_models
    input = safe_get(req, 'input', [])
    if not isinstance(input, list):
        input = [input]
    model = safe_get(req, 'model')
    # 如果model为none或者不存在于model_paths中，则使用默认模型
    if model is None or model not in models:
        model = "bge-large-zh-v1.5"
    embeddings = models[model]
    embed_datas = embeddings.embed_documents(input)
    data = []
    num_tokens = cal_tokens(input,"text-embedding-ada-002")
    # 遍历embed_datas，转化为embed_data格式后，添加到data中
    for i, embed_data in enumerate(embed_datas):
        data.append({
            "object": "embedding",
            "index": i,
            "embedding": embed_data
        })
    resp = {
        "object": "list",
        "data": data,
        "model": model,
        "usage": {
            "prompt_tokens": num_tokens,
            "total_tokens": num_tokens
        }
    }
    return sanic_json(resp)












