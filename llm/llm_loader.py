from langchain_community.chat_models import QianfanChatEndpoint 
from langchain_community.llms.tongyi import Tongyi
from langchain_community.llms.sparkllm import SparkLLM
from langchain_community.llms.baidu_qianfan_endpoint import QianfanLLMEndpoint
from langchain_community.chat_models import QianfanChatEndpoint,ChatTongyi,ChatSparkLLM,ChatZhipuAI
from langchain.llms.base import LLM
from langchain_core.language_models.chat_models import BaseChatModel

from llm.adaptor.chat2llm import Chat2LLM

from utils.general_utils import *

modal_list={
    "qianfan":["ERNIE-Bot-4","ERNIE-Speed-128K","ERNIE-Speed-8K","ERNIE-Lite-8K"],
    "tongyi":["qwen-plus","qwen-turbo"],
    "zhipu":["glm-4"],
    "spark":["spark-1.1","spark-2.1","spark-3.1"],
    "proxy":["gpt-3.5-turbo","gpt-4","gpt-4o","gpt-4o-2024-05-13"],
}


spark_dict={"spark-1.1":["general","ws://spark-api.xf-yun.com/v1.1/chat"],
            "spark-2.1":["generalv2","ws://spark-api.xf-yun.com/v2.1/chat"],
            "spark-3.1":["generalv3","ws://spark-api.xf-yun.com/v3.1/chat"],
            }

modal_type_dict = {item: key for key, sublist in modal_list.items() for item in sublist}


# 大模型定义


def getLLM(model,temperature=0.1)->LLM:
    if not model in modal_type_dict:
        model = "spark-3.1"
    type = modal_type_dict[model]
    if type == "qianfan":
        if get_config('llm','qf_ak'):
            return QianfanLLMEndpoint(qianfan_ak=get_config('llm','qf_ak'),qianfan_sk=get_config('llm','qf_sk'),model=model,temperature=temperature)
        else:
            raise Exception("qianfan_ak not set .Please check config.ini")
    elif type == "spark":
        if get_config('llm','xh_app_id'):
            return SparkLLM(spark_app_id=get_config('llm','xh_app_id'),spark_api_key=get_config('llm','xh_api_key'),spark_api_secret=get_config('llm','xh_api_secret'),spark_llm_domain=spark_dict[model][0],spark_api_url=spark_dict[model][1])
        else:
            raise Exception("spark_app_id not set .Please check config.ini")
    elif type == "tongyi":
        if get_config('llm','ty_api_key'):
            return Tongyi(dashscope_api_key = get_config('llm','ty_api_key'),model_name=model,temperature=temperature)
        else:
            raise Exception("ty_api_key not set .Please check config.ini")
    elif type == 'zhipu':
        if get_config('llm','zhipu_key'):
            return Chat2LLM(chat = ChatZhipuAI(zhipuai_api_key=get_config('llm','zhipu_key'),model_name=model,temperature=temperature))
        else:
            raise Exception("zhipu_key not set .Please check config.ini")
        
def getChat(model,temperature=0.1)->BaseChatModel:
    type = modal_type_dict[model]
    if type == "qianfan":
        if get_config('llm','qf_ak'):
            return QianfanChatEndpoint(qianfan_ak=get_config('llm','qf_ak'),qianfan_sk=get_config('llm','qf_sk'),model=model,temperature=temperature)
        else:
            raise Exception("qianfan_ak not set .Please check config.ini")
    elif type == "spark":
        if get_config('llm','xh_app_id'):
            return ChatSparkLLM(spark_app_id=get_config('llm','xh_app_id'),spark_api_key=get_config('llm','xh_api_key'),spark_api_secret=get_config('llm','xh_api_secret'),spark_llm_domain=spark_dict[model][0],spark_api_url=spark_dict[model][1])
        else:
            raise Exception("spark_app_id not set .Please check config.ini")
    elif type == "tongyi":
        if get_config('llm','ty_api_key'):
            return ChatTongyi(dashscope_api_key = get_config('llm','ty_api_key'),model_name=model,temperature=temperature)
        else:
            raise Exception("ty_api_key not set .Please check config.ini")
    elif type == 'zhipu':
        if get_config('llm','zhipu_key'):
            return ChatZhipuAI(zhipuai_api_key=get_config('llm','zhipu_key'),model_name=model,temperature=temperature)
        else:
            raise Exception("zhipu_key not set .Please check config.ini")
