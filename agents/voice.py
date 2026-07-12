from langchain_openai import ChatOpenAI
from crewai import Agent

def create_voice_agent(llm=None):
    if llm is None:
        llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.7)
    
    return Agent(
        role="Voiceover Specialist",
        goal="Tạo text voiceover và setting giọng nói cho ElevenLabs",
        backstory="Chuyên gia làm voice bé gái 3-4 tuổi, giọng ngọng nhẹ, dễ thương, giàu cảm xúc.",
        chat_llm=llm,
        verbose=False,
        max_iter=10
    )