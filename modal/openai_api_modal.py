import time
import uuid
def get_chat_resp(model):   
    return {
            "id": uuid.uuid4().hex,
            "object": "chat.completion",
            "created": time.time(),
            "model": model,
            "system_fingerprint": "",
            "choices": [{
                "index": 0,
                "message": {
                "role": "assistant",
                "content": "",
                "tool_calls":"",
                },
                "logprobs": '',
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
def get_chat_stream_resp(model):     
    return {
                    "id": uuid.uuid4().hex,
                    "object": "chat.completion.chunk",
                    "created": time.time(),
                    "model": model,
                    "system_fingerprint": "",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "role": "assistant",
                                "content": ""
                            },
                            "logprobs": '',
                            "finish_reason": ""
                        }
                    ],
                    "usage": {
                        "completion_tokens": 0,
                        "prompt_tokens": 0,
                        "total_tokens": 0
                    }
                }
def get_completions_resp(model):    
    return {
            "choices": [
                {
                "finish_reason": "length",
                "index": 0,
                "logprobs": '',
                "text": ""
                }
            ],
            "created": time.time(),
            "id": uuid.uuid4().hex,
            "model": model,
            "object": "text_completion",
            "usage": {
                "completion_tokens": 0,
                "prompt_tokens": 0,
                "total_tokens": 0
            }
        }
    
def get_completions_stream_resp(model):    
    return {
            "choices": [
                {
                    "finish_reason": "",
                    "index": 0,
                    "logprobs": '',
                    "delta": {
                                "content": ""
                            },
                }
            ],
            "created":  time.time(),
            "id": uuid.uuid4().hex,
            "model": model,
            "object": "text_completion",
            "usage": {
                "completion_tokens": 0,
                "prompt_tokens": 0,
                "total_tokens": 0
            }
        }