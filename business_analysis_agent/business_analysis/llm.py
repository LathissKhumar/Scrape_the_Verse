import os
import re
import json
from typing import Any, Optional, Type, TypeVar, List, Dict, get_origin, get_args
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
            temperature=0.0,
            format="json",
            num_ctx=1536,
            num_predict=384,
            keep_alive="1h",
            timeout=60,
        )
    return _llm_instance


def clean_json_string(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    # Remove reasoning blocks like ...```
    cleaned = re.sub(r'```.*?```', '', text, flags=re.DOTALL).strip()
    
    # Try finding markdown code block ```json ... ``` or ``` ... ```
    match = re.search(r'```(?:json)?\s*(\{.*\}|\[.*\])\s*```', cleaned, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Try finding raw json object { ... } or array [ ... ]
    match_braces = re.search(r'(\{.*\}|\[.*\])', cleaned, re.DOTALL)
    if match_braces:
        return match_braces.group(1).strip()
    
    return cleaned


def _get_field_default(field_info: Any, field_name: str) -> Any:
    """Get default value for a field, handling various annotation types."""
    if field_info.default is not PydanticUndefined and field_info.default is not None:
        return field_info.default
    if field_info.default_factory is not None:
        return field_info.default_factory()
    
    annotation = field_info.annotation
    origin = get_origin(annotation)
    args = get_args(annotation)
    
    if annotation == str or origin is str or (origin is None and str(annotation) == "str"):
        return "Not specified"
    if annotation == int or annotation == float or origin in (int, float):
        return 0
    if annotation == bool or origin is bool:
        return False
    if origin is list or origin is List:
        return []
    if origin is dict or origin is Dict:
        return {}
    if origin is Optional or annotation == Optional[str]:
        return None
    return "Not specified"


def create_fallback_model_instance(model_class: Type[T]) -> T:
    """Create a fallback instance for a Pydantic model class (not list)."""
    if not isinstance(model_class, type) or not issubclass(model_class, BaseModel):
        raise TypeError(f"Expected Pydantic BaseModel class, got {type(model_class)}")
    
    fields = model_class.model_fields
    fallback_data = {}
    for field_name, field_info in fields.items():
        fallback_data[field_name] = _get_field_default(field_info, field_name)
    
    try:
        return model_class.model_validate(fallback_data)
    except Exception:
        return model_class.model_construct(**fallback_data)


def validate_structured_output(output_model: Type[T], data: Any, max_retries: int = 1) -> tuple[Optional[T], Optional[str]]:
    """
    Validate structured output against Pydantic model.
    Returns (validated_instance, error_message).
    """
    for attempt in range(max_retries + 1):
        try:
            if isinstance(data, output_model):
                return data, None
            if isinstance(data, dict):
                return output_model.model_validate(data), None
            if isinstance(data, str):
                return output_model.model_validate_json(data), None
            # Try to construct from whatever we got
            return output_model.model_validate(data), None
        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries and isinstance(data, str):
                # Try to clean and re-parse
                cleaned = clean_json_string(data)
                if cleaned != data:
                    data = cleaned
                    continue
            return None, error_msg
    return None, error_msg


class RobustStructuredLLM(Runnable):
    def __init__(self, llm: ChatOllama, output_model: Type[T]):
        self.llm = llm
        self.output_model = output_model
        # Use direct format="json" validation for ChatOllama (prevents with_structured_output hangs)
        self.structured_llm = None

    def invoke(self, input: Any, config: Any = None, **kwargs: Any) -> T:
        # Try structured output first
        if self.structured_llm is not None:
            try:
                res = self.structured_llm.invoke(input, config=config, **kwargs)
                if res is not None:
                    validated, err = validate_structured_output(self.output_model, res)
                    if validated is not None:
                        return validated
            except Exception:
                pass

        # Fallback: raw LLM + manual validation with retry
        try:
            schema_dict = self.output_model.model_json_schema()
            schema_dict.pop("title", None)
            schema_dict.pop("description", None)
            schema_json = json.dumps(schema_dict, separators=(",", ":"))
            extra_prompt = f"\n\nCRITICAL: Return ONLY a valid raw JSON object strictly conforming to this schema:\n{schema_json}"
            
            if isinstance(input, str):
                prompt = input + extra_prompt
            else:
                prompt = str(input) + extra_prompt

            raw_res = self.llm.invoke(prompt, config=config, **kwargs)
            raw_text = raw_res.content if hasattr(raw_res, "content") else str(raw_res)
            
            validated, err = validate_structured_output(self.output_model, raw_text, max_retries=1)
            if validated is not None:
                return validated
            
            # If validation failed, capture error for state
            raise ValueError(f"Structured output validation failed after retry: {err}")
        except Exception as e:
            # Return fallback but mark as validation error
            fallback = create_fallback_model_instance(self.output_model)
            # Attach validation error metadata if possible
            if hasattr(fallback, '_validation_error'):
                fallback._validation_error = str(e)
            return fallback

    async def ainvoke(self, input: Any, config: Any = None, **kwargs: Any) -> T:
        if self.structured_llm is not None:
            try:
                res = await self.structured_llm.ainvoke(input, config=config, **kwargs)
                if res is not None:
                    validated, err = validate_structured_output(self.output_model, res)
                    if validated is not None:
                        return validated
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
            
            validated, err = validate_structured_output(self.output_model, raw_text, max_retries=1)
            if validated is not None:
                return validated
            
            raise ValueError(f"Structured output validation failed after retry: {err}")
        except Exception as e:
            fallback = create_fallback_model_instance(self.output_model)
            if hasattr(fallback, '_validation_error'):
                fallback._validation_error = str(e)
            return fallback


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