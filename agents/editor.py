from langchain_openai import ChatOpenAI
from crewai import Agent

def create_editor_agent(llm=None):
    if llm is None:
        llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.7)
    
    return Agent(
        role="Video Editor",
        goal="Hướng dẫn ghép video, voice, nhạc nền và hiệu ứng trong CapCut",
        backstory="Chuyên gia edit video TikTok/Reel, biết dùng AI lip sync, beat sync, text overlay.",
        chat_llm=llm,
        verbose=False,
        max_iter=10
    )