* **下载向量和rerank模型**

```
# 下载安装git-fls https://github.com/git-lfs/git-lfs/releases
git lfs install

mkdir -p modal
cd modal

git clone https://www.modelscope.cn/quietnight/bge-reranker-large.git
git clone https://www.modelscope.cn/AI-ModelScope/bge-large-zh-v1.5.git
```

- **配置llm，复制config-exp.ini**

```
cp config-exp.ini config.ini 
```

- **配置核心字段（最简版，除标注须替换的字段外，其他字段不动）**

```
# 复制本文件并命名 config.ini

[llm]


# https://console.xfyun.cn/services/cbm
# 讯飞星火 app id
xh_app_id = 
# 讯飞星火 api secret
xh_api_secret = 
# 讯飞星火 api key
xh_api_key = 



[embedding]
bge_embedding_path = 

[rerank]
bge_reranker_path =

```

* **拉取项目，安装依赖**

```
# 进入项目主目录
cd lang2openai
# 创建虚拟环境
python -m venv venv
# 激活虚拟环境win10
venv\Scripts\activate
# 激活虚拟环境linux
source venv/bin/activate
# 后端依赖安装
pip install -r requirements.txt
```

* **启动项目**

```
# python 3.10以上版本
python main.py
```

- **访问接口**

```
curl --location --request POST 'http://127.0.0.1:8778/v1/completions' \
--header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
--header 'Content-Type: application/json' \
--header 'Accept: */*' \
--header 'Host: 127.0.0.1:8778' \
--header 'Connection: keep-alive' \
--data-raw '{
    "model": "spark-3.1",
    "prompt": "你能做什么？",
    "stream":false
  }'
```

