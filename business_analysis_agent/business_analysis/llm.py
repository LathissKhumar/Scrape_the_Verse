import os
import re
import json
from typing import Any, Optional, Type, TypeVar
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=BaseModel)

_llm_instance: Optional[ChatOllama] = None


def get_llm() -> ChatOllama:
    global _llm_instance
    if _llm_instance is None:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "qwen3:4b")
        _llm_instance = ChatOllama(
            base_url=base_url,
            model=model,
            temperature=0.1,
            num_ctx=4096,
            num_predict=1024,
            keep_alive="1h",
            timeout=120,
        )
    return _llm_instance


def clean_json_string(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    # Remove reasoning blocks like <think>...</think>
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    
    # Try finding markdown code block ```json ... ``` or ``` ... ```
    match = re.search(r'```(?:json)?\s*(\{.*\}|\[.*\])\s*```', cleaned, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Try finding raw json object { ... } or array [ ... ]
    match_braces = re.search(r'(\{.*\}|\[.*\])', cleaned, re.DOTALL)
    if match_braces:
        return match_braces.group(1).strip()
    
    return cleaned


def create_fallback_model_instance(model_class: Type[T]) -> T:
    fields = model_class.model_fields
    fallback_data = {}
    for field_name, field_info in fields.items():
        if field_info.default is not PydanticUndefined and field_info.default is not None:
            fallback_data[field_name] = field_info.default
        elif field_info.default_factory is not None:
            fallback_data[field_name] = field_info.default_factory()
        else:
            annotation = field_info.annotation
            if annotation == str or annotation == Optional[str]:
                fallback_data[field_name] = "Not specified"
            elif annotation == int or annotation == float:
                fallback_data[field_name] = 0
            elif annotation == bool:
                fallback_data[field_name] = False
            elif getattr(annotation, "__origin__", None) is list:
                fallback_data[field_name] = []
            elif getattr(annotation, "__origin__", None) is dict:
                fallback_data[field_name] = {}
            else:
                fallback_data[field_name] = "Not specified"
    try:
        return model_class.model_validate(fallback_data)
    except Exception:
        return model_class.model_construct(**fallback_data)


class RobustStructuredLLM(Runnable):
    def __init__(self, llm: ChatOllama, output_model: Type[T]):
        self.llm = llm
        self.output_model = output_model
        try:
            self.structured_llm = llm.with_structured_output(output_model)
        except Exception:
            self.structured_llm = None

    def invoke(self, input: Any, config: Any = None, **kwargs: Any) -> T:
        if self.structured_llm is not None:
            try:
                res = self.structured_llm.invoke(input, config=config, **kwargs)
                if res is not None:
                    return res
            except Exception:
                pass

        # Fallback parsing with raw LLM invocation
        try:
            schema_json = json.dumps(self.output_model.model_json_schema(), indent=2)
            extra_prompt = f"\n\nCRITICAL: Return ONLY a valid raw JSON object strictly conforming to this schema:\n{schema_json}"
            
            if isinstance(input, str):
                prompt = input + extra_prompt
            else:
                prompt = str(input) + extra_prompt

            raw_res = self.llm.invoke(prompt, config=config, **kwargs)
            raw_text = raw_res.content if hasattr(raw_res, "content") else str(raw_res)
            json_str = clean_json_string(raw_text)
            if json_str:
                return self.output_model.model_validate_json(json_str)
        except Exception:
            pass

        return create_fallback_model_instance(self.output_model)

    async def ainvoke(self, input: Any, config: Any = None, **kwargs: Any) -> T:
        if self.structured_llm is not None:
            try:
                res = await self.structured_llm.ainvoke(input, config=config, **kwargs)
                if res is not None:
                    return res
            except Exception:
                pass

        try:
            schema_json = json.dumps(self.output_model.model_json_schema(), indent=2)
            extra_prompt = f"\n\nCRITICAL: Return ONLY a valid raw JSON object strictly conforming to this schema:\n{schema_json}"
            
            if isinstance(input, str):
                prompt = input + extra_prompt
            else:
                prompt = str(input) + extra_prompt

            raw_res = await self.llm.ainvoke(prompt, config=config, **kwargs)
            raw_text = raw_res.content if hasattr(raw_res, "content") else str(raw_res)
            json_str = clean_json_string(raw_text)
            if json_str:
                return self.output_model.model_validate_json(json_str)
        except Exception:
            pass

        return create_fallback_model_instance(self.output_model)


def get_structured_llm(output_model: Type[T]) -> RobustStructuredLLM:
    llm = get_llm()
    return RobustStructuredLLM(llm, output_model)


def invoke_llm(prompt: str, output_model: Optional[Type[T]] = None) -> Any:
    if output_model:
        structured_llm = get_structured_llm(output_model)
        return structured_llm.invoke(prompt)
    llm = get_llm()
    return llm.invoke(prompt)


async def ainvoke_llm(prompt: str, output_model: Optional[Type[T]] = None) -> Any:
    if output_model:
        structured_llm = get_structured_llm(output_model)
        return await structured_llm.ainvoke(prompt)
    llm = get_llm()
    return await llm.ainvoke(prompt)