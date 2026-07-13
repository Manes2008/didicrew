# MIT License
# Copyright (c) 2026 Manes2008/didicrew

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(provider: str, model_name: str, api_key: str, temperature: float = 0.75):
    """
    Khởi tạo đối tượng Chat LLM tương ứng dựa trên provider và model name.
    """
    if provider == "OpenAI":
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
    elif provider == "Google Gemini":
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key
        )
    raise ValueError(f"Không hỗ trợ nhà cung cấp LLM: {provider}")
