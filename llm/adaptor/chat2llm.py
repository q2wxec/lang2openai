# -*- coding: utf-8 -*-
from typing import Any, List, Mapping, Optional,Iterator
from langchain_core.outputs import  GenerationChunk
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain_core.language_models.chat_models import BaseChatModel


class Chat2LLM(LLM):
    chat:BaseChatModel
    
    @property
    def _llm_type(self) -> str:
        return "Chat2LLM"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"chat": self.chat}
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        return self.chat.invoke(prompt).content

                
    def _stream(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
        ) -> Iterator[GenerationChunk]:
                resp = self.chat.stream(prompt)
                for part in resp:
                    chunk = GenerationChunk(text=part.content)
                    yield chunk