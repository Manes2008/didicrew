# core/workflow.py
from agents.script import create_script_agent
from agents.visual import create_visual_agent
from agents.voice import create_voice_agent
from agents.editor import create_editor_agent
from agents.image import create_image_agent

from crewai import Task

def run_stage(stage_name: str, idea: str, previous_result: str = None, llm=None):
    try:
        if stage_name == "script":
            agent = create_script_agent(llm)
            task = Task(
                description=f"Viết kịch bản TikTok 25-30s cho ý tưởng: {idea}",
                expected_output="Kịch bản đầy đủ có hook, lời thoại bé gái, timing rõ ràng",
                agent=agent
            )
            return agent.execute_task(task)

        elif stage_name == "visual":
            agent = create_visual_agent(llm)
            task = Task(
                description=f"Dựa trên kịch bản sau, tạo prompt chi tiết cho Kling/Leonardo: {previous_result}",
                expected_output="Prompt chi tiết, có character reference",
                agent=agent
            )
            return agent.execute_task(task)
        
        elif stage_name == "image":
            agent = create_image_agent(llm)
            task = Task(
                description=f"Dựa trên kịch bản, tạo prompt và generate hình ảnh cho bé gái bằng gpt-image-2: {idea}",
                expected_output="Prompt + Link hình ảnh được tạo",
                agent=agent
            )
            return agent.execute_task(task)

        elif stage_name == "voice":
            agent = create_voice_agent(llm)
            task = Task(
                description=f"Tạo text voiceover giọng bé gái dễ thương cho kịch bản: {previous_result}",
                expected_output="Text voiceover + setting ElevenLabs",
                agent=agent
            )
            return agent.execute_task(task)

        elif stage_name == "editor":
            agent = create_editor_agent(llm)
            task = Task(
                description=f"Hướng dẫn chi tiết ghép video trong CapCut từ kịch bản: {previous_result}",
                expected_output="Hướng dẫn từng bước trong CapCut",
                agent=agent
            )
            return agent.execute_task(task)

        return "Stage chưa hỗ trợ"
    except Exception as e:
        return f"❌ Lỗi stage {stage_name}: {str(e)}"