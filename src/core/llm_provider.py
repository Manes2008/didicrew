# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import os
import config
from crewai import LLM

def get_llm(provider: str, model_name: str, api_key: str = None, temperature: float = 0.75):
    """
    Khoi tao doi tuong Chat LLM tuong ung dua tren provider va model name su dung Native CrewAI LLM.
    Tu dong nhan dien va sua loi lech Model Name <-> Provider.
    """
    p_lower = (provider or "").lower()
    m_lower = (model_name or "").lower()

    # Tu dong phat hien loai model dua vao ten
    is_gemini_model = "gemini" in m_lower or "gemini" in p_lower
    if "gpt" in m_lower or "o1" in m_lower or "o3" in m_lower:
        is_gemini_model = False

    if is_gemini_model:
        key = api_key or config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if key:
            os.environ["GEMINI_API_KEY"] = key
            
        clean_model = model_name if "gemini" in m_lower else "gemini-3.6-flash"
        clean_model = clean_model.replace("gemini/", "")
        
        # Chuyen cac model cu / deprecated sang phien ban moi nhat cua Google
        if clean_model in ("gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"):
            clean_model = "gemini-3.6-flash"
        elif clean_model in ("gemini-1.5-pro", "gemini-2.0-pro"):
            clean_model = "gemini-3.1-pro-preview"
            
        model_str = f"gemini/{clean_model}"
        
        return LLM(
            model=model_str,
            temperature=temperature,
            api_key=key
        )
    else:
        key = api_key or config.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if key:
            os.environ["OPENAI_API_KEY"] = key
            
        clean_model = model_name if ("gpt" in m_lower or "o1" in m_lower) else "gpt-4o-mini"
        clean_model = clean_model.replace("openai/", "")
        model_str = f"openai/{clean_model}"
        
        return LLM(
            model=model_str,
            temperature=temperature,
            api_key=key
        )
