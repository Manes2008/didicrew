from langchain_openai import ChatOpenAI
from crewai import Agent
from crewai.tools import tool
from openai import OpenAI
import os

@tool("genimage")
def generate_gpt_image(prompt: str) -> str:
    """Tạo hình ảnh bằng gpt-image-1-mini và trả về chuỗi base64."""
    try:
        client = OpenAI()
        response = client.images.generate(
            model="gpt-image-1-mini",
            prompt=prompt[:4000],
            size="1024x1024",
            quality="medium",
            n=1,
        )
        # Chỉ trả về chuỗi mã hóa thuần túy để frontend dễ bắt
        return response.data[0].b64_json
    except Exception as e:
        return f"ERROR: {str(e)}"

def create_image_agent(llm=None):
    if llm is None:
        llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.8)
    
    return Agent(
        role="Image Generation Specialist",
        goal="Tạo prompt và generate hình ảnh bằng gpt-image-2",
        backstory="Bạn là chuyên gia tạo hình ảnh bé gái Việt Nam 3 tuổi, da trắng, mắt to, tóc hai đuôi gà hồng, phong cách tiểu thư đáng yêu, cực kỳ chi tiết.",
        chat_llm=llm,
        tools=[generate_gpt_image],
        verbose=True,
        allow_delegation=False
    )