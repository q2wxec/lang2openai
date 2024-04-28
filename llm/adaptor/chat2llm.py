# -*- coding: utf-8 -*-
from typing import Any, List, Mapping, Optional,Iterator
from langchain_core.outputs import  GenerationChunk
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage


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
        chat_message = HumanMessage(content=prompt)
        return self.chat.invoke([chat_message]).content

                
    def _stream(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
        ) -> Iterator[GenerationChunk]:
                chat_message = HumanMessage(content=prompt)
                resp = self.chat.stream([chat_message])
                for part in resp:
                    chunk = GenerationChunk(text=part.content)
                    yield chunk