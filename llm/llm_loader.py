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
    "zhipu":["glm-4","glm-4-plus","glm-4-flash"],
    "spark":["general","generalv3","pro-128k","generalv3.5","4.0Ultra"],
    "proxy":["gpt-3.5-turbo","gpt-4","gpt-4o","gpt-4o-2024-05-13","gpt-4o-2024-08-06","gpt-4o-mini-2024-07-18"],
    "moonshot":["moonshot-v1-8k","moonshot-v1-32k","moonshot-v1-128k"],
}

modal_type_dict = {item: key for key, sublist in modal_list.items() for item in sublist}


# 大模型定义


def getLLM(model,temperature=0.1)->LLM:
    type = modal_type_dict[model]
    if type == "qianfan":
        if get_config('llm','qf_ak'):
            return QianfanLLMEndpoint(qianfan_ak=get_config('llm','qf_ak'),qianfan_sk=get_config('llm','qf_sk'),model=model,temperature=temperature)
        else:
            raise Exception("qianfan_ak not set .Please check config.ini")
        
def getChat(model,temperature=0.1)->BaseChatModel:
    type = modal_type_dict[model]
    if type == "qianfan":
        if get_config('llm','qf_ak'):
            return QianfanChatEndpoint(qianfan_ak=get_config('llm','qf_ak'),qianfan_sk=get_config('llm','qf_sk'),model=model,temperature=temperature)
        else:
            raise Exception("qianfan_ak not set .Please check config.ini")
