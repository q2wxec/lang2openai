from sanic.response import json as sanic_json
from sanic import request
import uuid

from utils.general_utils import *

def get_rerank_dict()->dict:
    from FlagEmbedding import FlagReranker
    result = {}
    if get_config('rerank','bge_reranker_path'):
        result['bge-reranker-large'] = FlagReranker(model_name_or_path=get_config('rerank','bge_reranker_path'), use_fp16=True)
    return result

async def rerank(req: request):
    models = req.app.ctx.reranke_models
    query = safe_get(req, 'query')
    documents = safe_get(req, 'documents', [])
    model = safe_get(req, 'model')
    # 如果model为none或者不存在于model_paths中，则使用默认模型
    if model is None or model not in models:
        model = "bge-reranker-large"
    reranker = models[model]
    sentence_pairs = [[query, passage] for passage in documents]
    scores = reranker.compute_score(sentence_pairs)
    results = []
    # 循环scores，documents，生成result并放入results中
    
    for i, (score, document) in enumerate(zip(scores, documents)):
    # 生成并添加 result 到 results 列表中
        results.append({
            "index": i,
            "relevance_score": (score+10)/20,
            "document": document
        })
    resp={
        "id":  uuid.uuid4().hex,
        "results": results
    }
    return sanic_json(resp)



