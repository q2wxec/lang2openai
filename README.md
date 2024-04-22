### 1.项目是做什么的？

通过LangChain标准化适配的llm，embedding，rerank，等实现，通过适配层，按openai-api统一的接口标准对外提供服务。

### 2.有那么多中间适配层的项目，为什么要用你的

市面上确实有很多api统一适配的项目比如one-api，我们的项目优势有如下几点：

- 简单，只做接口协议转换，因而本项目非常简单，没有任何中间件或数据库的依赖，可以说拿到代码，配置key之后就能使用
- RAG，市面上几乎所有的api统一适配项目都只是进行了对话接口协议的适配，本项目针对RAG类型的项目额外进行了embedding，rerank的接口协议适配与实现，需要按说明将模型文件下载到本地目录，即可直接使用
- 可进化，因为本项目最终是基于LangChain标准化来实现外部接口调用的，因而一切LangChain自身或厂商适配过的模型，本项目都支持，而作为大语言模型应用开发的当红炸子鸡框架，我相信，其支持的模型调用必然会越来约多。目前已支持的见此链接[Chat models | 🦜️🔗 LangChain](https://python.langchain.com/docs/integrations/chat/?ref=blog.langchain.dev)
- function calling，考虑到越来越多的agents以及工具调用的需求产生，本项目特意基于提示词工程的方式实现了openai-api的function calling适配，目前以spark-3.1作为底层模型进行测试，效果良好。

### 3.接口一览

- /v1/completions

  - request

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

  - response

  ```
  {
      "choices": [
          {
              "finish_reason": "length",
              "index": 0,
              "logprobs": "",
              "text": "作为一个认知智能模型，我可以回答你的问题、提供信息和建议、进行自然语言处理和生成文本等。以下是一些我可以做的事情：\n  * 回答各种问题，包括常见问题、学术问题、技术问题等。\n  * 提供各种领域的知识和信息，例如历史、科学、文化、艺术等。\n  * 给出建议和指导，例如如何学习一门新技能、如何解决某个问题等。\n  * 进行自然语言处理和生成文本，例如翻译、摘要、对话等。\n当然，我的能力也是有限的，有些问题可能超出了我的能力范围或者我没有足够的信息来回答。如果您有任何疑问或需要帮助，请随时告诉我。"
          }
      ],
      "created": 1713772029.4484026,
      "id": "513a06f4bccc4bb3a563c494bab952ab",
      "model": "spark-3.1",
      "object": "text_completion",
      "usage": {
          "completion_tokens": 244,
          "prompt_tokens": 8,
          "total_tokens": 252
      }
  }
  ```

  

- /v1/chat/completions

  - request

  ```
  curl --location --request POST 'http://127.0.0.1:8778/v1/chat/completions' \
  --header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
  --header 'Content-Type: application/json' \
  --header 'Accept: */*' \
  --header 'Host: 127.0.0.1:8778' \
  --header 'Connection: keep-alive' \
  --data-raw '{
    "model": "spark-3.1",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Hello!"
      }
    ]
  }'
  ```

  - response

  ```
  {
      "id": "33e10d6cb5b34c149b38178dccfa9e05",
      "object": "chat.completion",
      "created": 1713772263.898054,
      "model": "spark-3.1",
      "system_fingerprint": "",
      "choices": [
          {
              "index": 0,
              "message": {
                  "role": "assistant",
                  "content": "Hello! How can I assist you today?",
                  "tool_calls": ""
              },
              "logprobs": "",
              "finish_reason": "stop"
          }
      ],
      "usage": {
          "prompt_tokens": 8,
          "completion_tokens": 9,
          "total_tokens": 17
      }
  }
  ```

  

- /v1/chat/completions（function call）

  - request

  ```
  {
    "model": "spark-3.1",
    "messages": [
      {
        "role": "user",
        "content": "What's the weather like in Boston today?"
      }
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_current_weather",
          "description": "Get the current weather in a given location",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA"
              },
              "unit": {
                "type": "string",
                "enum": [
                  "celsius",
                  "fahrenheit"
                ]
              }
            },
            "required": [
              "location"
            ]
          }
        }
      }
    ],
    "tool_choice": "auto"
  }
  ```

  - response

  ```
  {
      "id": "d121afe229164872b20d3123a41b3d48",
      "object": "chat.completion",
      "created": 1713772368.84041,
      "model": "spark-3.1",
      "system_fingerprint": "",
      "choices": [
          {
              "index": 0,
              "message": {
                  "role": "assistant",
                  "content": "",
                  "tool_calls": [
                      {
                          "id": "a0366c69f7c24c0d92bfc598457fca48",
                          "type": "function",
                          "function": {
                              "name": "get_current_weather",
                              "arguments": "{\"location\": \"Boston, MA\"}"
                          }
                      }
                  ]
              },
              "logprobs": "",
              "finish_reason": "stop"
          }
      ],
      "usage": {
          "prompt_tokens": 9,
          "completion_tokens": 28,
          "total_tokens": 37
      }
  }
  ```

  

- /v1/embeddings

  - request

  ```
  curl --location --request POST 'http://127.0.0.1:8778/v1/embeddings' \
  --header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
  --header 'Content-Type: application/json' \
  --header 'Accept: */*' \
  --header 'Host: 127.0.0.1:8778' \
  --header 'Connection: keep-alive' \
  --data-raw '{
      "input": "Your text string goes here",
      "model": "bge-large-zh-v1.5"
  }'
  ```

  - response

  ```
  {
      "object": "list",
      "data": [
          {
              "object": "embedding",
              "index": 0,
              "embedding": [
                  -0.024587785825133324,
                  -0.018740979954600334,
                 ...
                  0.016061244532465935
              ]
          }
      ],
      "model": "bge-large-zh-v1.5",
      "usage": {
          "prompt_tokens": 5,
          "total_tokens": 5
      }
  }
  ```

  

- /v1/rerank

  - request

  ```
  curl --location --request POST 'http://127.0.0.1:8778/v1/rerank' \
  --header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
  --header 'Content-Type: application/json' \
  --header 'Accept: */*' \
  --header 'Host: 127.0.0.1:8778' \
  --header 'Connection: keep-alive' \
  --data-raw '{
      "model": "bge-reranker-large",
      "query": "A man is eating pasta.",
      "documents": [
          "A man is eating food.",
          "A man is eating a piece of bread.",
          "The girl is carrying a baby.",
          "A man is riding a horse.",
          "A woman is playing violin.",
          "A man is eating pasta.",
          "A man is eating pasta",
          "A man is eating "
      ]
    }'
  ```

  - response

  ```
  {
      "id": "9a5b0cc3947a45348cef53bf3ff6d449",
      "results": [
          {
              "index": 0,
              "relevance_score": 0.9754678249359131,
              "document": "A man is eating food."
          },
          {
              "index": 1,
              "relevance_score": 0.3509412884712219,
              "document": "A man is eating a piece of bread."
          },
          {
              "index": 2,
              "relevance_score": 0.02600417137145996,
              "document": "The girl is carrying a baby."
          },
          {
              "index": 3,
              "relevance_score": 0.02587881088256836,
              "document": "A man is riding a horse."
          },
          {
              "index": 4,
              "relevance_score": 0.026003408432006835,
              "document": "A woman is playing violin."
          },
          {
              "index": 5,
              "relevance_score": 0.9765342235565185,
              "document": "A man is eating pasta."
          },
          {
              "index": 6,
              "relevance_score": 0.9765145778656006,
              "document": "A man is eating pasta"
          },
          {
              "index": 7,
              "relevance_score": 0.9709453105926513,
              "document": "A man is eating "
          }
      ]
  }
  ```

  