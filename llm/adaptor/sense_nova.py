# -*- coding: utf-8 -*-
import sensenova
from typing import Any, List, Mapping, Optional,Iterator
from langchain_core.outputs import  GenerationChunk
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM


class SenseNovaLLM(LLM):
    st_ak: Optional[str] = None
    st_sk: Optional[str] = None
    model: Optional[str] = None

    @property
    def _llm_type(self) -> str:
        return "SenseNovaLLM"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"ak": self.st_ak,"sk":self.st_sk}
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        sensenova.access_key_id = self.st_ak
        sensenova.secret_access_key = self.st_sk
        stream = False # 流式输出或非流式输出
        model_id = self.model # 填写真实的模型ID

        resp = self.do_request(prompt, stream, model_id)

        return resp['data']["choices"][0]["message"]
                
    def _stream(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
        ) -> Iterator[GenerationChunk]:
                sensenova.access_key_id = self.st_ak
                sensenova.secret_access_key = self.st_sk
                stream = True # 流式输出或非流式输出
                model_id = self.model # 填写真实的模型ID

                resp = self.do_request(prompt, stream, model_id)
                for part in resp:
                    choices = part['data']["choices"]
                    for c_idx, c in enumerate(choices):
                        delta = c.get("delta")
                        chunk = GenerationChunk(text=delta)
                        yield chunk
                        if run_manager:
                            run_manager.on_llm_new_token(chunk.text)

    def do_request(self, prompt, stream, model_id):
        resp = sensenova.ChatCompletion.create(
            messages=[{"role": "user", "content": prompt}],
            model=model_id,
            stream=stream,
            max_new_tokens=1024,
            n=1,
            repetition_penalty=1.05,
            temperature=0.8,
            top_p=0.7,
            know_ids=[],
            user="sensenova-python-test-user",
            knowledge_config={
                "control_level": "normal",
                "knowledge_base_result": True,
                "knowledge_base_configs":[]
            },
            plugins={
                "associated_knowledge": {
                    "content": "需要注入给模型的知识",
                    "mode": "concatenate"
                },
                "web_search": {
                    "search_enable": True,
                    "result_enable": True
                },
            }
        )
        
        return resp