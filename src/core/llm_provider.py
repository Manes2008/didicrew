# MIT License
# Copyright (c) 2026 Manes2008/didicrew

from crewai import LLM

def get_llm(provider: str, model_name: str, api_key: str, temperature: float = 0.75):
    """
    Khoi tao doi tuong Chat LLM tuong ung dua tren provider va model name su dung Native CrewAI LLM.
    """
    if provider == "OpenAI":
        model_str = f"openai/{model_name}" if not model_name.startswith("openai/") else model_name
        return LLM(
            model=model_str,
            temperature=temperature,
            api_key=api_key
        )
    elif provider == "Google Gemini":
        model_str = f"gemini/{model_name}" if not model_name.startswith("gemini/") else model_name
        return LLM(
            model=model_str,
            temperature=temperature,
            api_key=api_key
        )
    raise ValueError(f"Khong ho tro nha cung cap LLM: {provider}")
