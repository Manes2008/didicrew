from langchain_openai import ChatOpenAI
from crewai import Agent

def create_visual_agent(llm=None):
    if llm is None:
        llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.7)
    
    return Agent(
        role="Visual Prompt Engineer",
        goal="Tạo prompt chi tiết chất lượng cao cho công cụ tạo hình ảnh/video",
        backstory="Chuyên gia tạo prompt cho bé gái Việt Nam 3 tuổi, da trắng, mắt to, tóc hai đuôi gà, phong cách tiểu thư đáng yêu.",
        chat_llm=llm,
        verbose=False,
        max_iter=10
    )