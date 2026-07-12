from langchain_openai import ChatOpenAI
from crewai import Agent

def create_script_agent(llm=None):
    if llm is None:
        llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.75)
    
    return Agent(
        role="Senior Script Writer",
        goal="Viết kịch bản TikTok/Reel 25-30s hấp dẫn, dễ thương",
        backstory="Bạn là chuyên gia viết content TikTok về bé gái tiểu thư đáng yêu, ngôn ngữ ngọng nhẹ, gần gũi, hook mạnh.",
        chat_llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=10
    )