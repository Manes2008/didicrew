# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import os
import yaml
from crewai import Task, Crew
from src.agents.factory import AgentFactory

class WorkflowEngine:
    """
    Bộ điều phối chính (Engine) chịu trách nhiệm chạy các Task tuần tự trong quy trình VideoCrew.
    """
    def __init__(self, tasks_config_path: str = None, agents_config_path: str = None):
        if tasks_config_path is None:
            tasks_config_path = os.path.join("config", "tasks.yaml")
            
        with open(tasks_config_path, "r", encoding="utf-8") as f:
            self.tasks_config = yaml.safe_load(f)
            
        self.agent_factory = AgentFactory(agents_config_path)
        
        # Ánh xạ từ tên stage sang agent_id và task_id trong file cấu hình
        self.stage_mapping = {
            "script": ("script_writer", "script_task"),
            "visual": ("visual_prompt_engineer", "visual_task"),
            "image": ("image_generation_specialist", "image_task"),
            "voice": ("voiceover_specialist", "voice_task"),
            "video": ("video_editor", "editor_task")  # Tạm giữ agent cho tương thích nếu cần, nhưng sẽ bị đè bởi code Python thuần
        }

    def run_stage(self, stage_name: str, idea: str, previous_result: str = None, llm=None, all_results: dict = None, context: dict = None) -> str:
        """
        Thực thi một stage cụ thể trong Workflow.
        """
        try:
            # Chạy trực tiếp sinh ảnh bằng code Python thuần túy không qua Agent
            if stage_name == "image":
                prompt = previous_result if previous_result else idea
                
                # Trích xuất prompt của Scene 1 và hồ sơ nhân vật/phong cách để sinh ảnh tối ưu
                import re
                scene1_match = re.search(r"(?:Scene|Cảnh)\s*1[\s*:\-–\.]+(.*?)(?=(?:Scene|Cảnh)\s*2[\s*:\-–\.]+|\Z)", prompt, re.DOTALL | re.IGNORECASE)
                if scene1_match:
                    profile_match = re.search(r"(?:Character Profile|Hồ sơ nhân vật|Profile|Nhân vật)[\s*:\-–\.]+(.*?)(?=(?:Art Style|Phong cách|Scene)\s*|\Z)", prompt, re.DOTALL | re.IGNORECASE)
                    style_match = re.search(r"(?:Art Style|Phong cách nghệ thuật|Style)[\s*:\-–\.]+(.*?)(?=(?:Scene|Nhân vật|Profile)\s*|\Z)", prompt, re.DOTALL | re.IGNORECASE)
                    
                    profile_text = profile_match.group(1).strip() if profile_match else ""
                    style_text = style_match.group(1).strip() if style_match else ""
                    scene1_text = scene1_match.group(1).strip()
                    
                    prompt = f"{style_text} {profile_text} {scene1_text}"
                    prompt = prompt.replace("\n", " ").strip()

                image_engine = context.get("image_engine", "openai") if context else "openai"
                if image_engine == "sd1.5_local":
                    from src.tools.image_tool import generate_local_image_sd_func
                    return generate_local_image_sd_func(prompt, use_gpu=False)
                elif image_engine == "markl_local":
                    from src.tools.image_tool import generate_local_image_sd_func
                    return generate_local_image_sd_func(prompt, use_gpu=True)
                else:
                    from src.tools.image_tool import generate_gpt_image_func
                    return generate_gpt_image_func(prompt)
                
            # Chạy trực tiếp sinh video
            if stage_name == "video":
                from src.tools.video_tool import generate_video_func
                
                # Ưu tiên lấy kịch bản chi tiết (visual prompt) thay vì chỉ câu ý tưởng ban đầu
                visual_result = all_results.get("visual", "") if all_results else ""
                script_result = all_results.get("script", "") if all_results else ""
                
                # Trích xuất toàn bộ danh sách đường dẫn ảnh từ kết quả bước 3
                image_result = all_results.get("image", "") if all_results else ""
                image_paths = []
                if image_result:
                    for line in image_result.split("\n"):
                        if "generated_images" in line:
                            path = line.replace("📁 Đường dẫn ảnh:", "").replace("📁 Đường dẫn ảnh: ", "").strip()
                            if path:
                                image_paths.append(path)

                # Trích xuất đường dẫn voiceover tu kết quả bước 4
                voice_result = all_results.get("voice", "") if all_results else ""
                voice_path = None
                if voice_result:
                    for line in voice_result.split("\n"):
                        if ".mp3" in line or ".wav" in line:
                            voice_path = line.strip()
                            break

                video_engine = context.get("video_engine", "wan2.1_local") if context else "wan2.1_local"
                prompt = visual_result if visual_result else (script_result if script_result else idea)
                
                # Truyền danh sách ảnh vào để mỗi phân cảnh sử dụng ảnh tương ứng
                return generate_video_func(prompt, image_path=image_paths, voice_path=voice_path, engine=video_engine)

            if stage_name not in self.stage_mapping:
                return f"Stage '{stage_name}' chưa được hỗ trợ."
                
            agent_id, task_id = self.stage_mapping[stage_name]
            
            # Khởi tạo Agent từ Factory và truyền ngữ cảnh động
            agent = self.agent_factory.create_agent(agent_id, llm, context)
            
            # Đọc cấu hình Task tương ứng
            task_cfg = self.tasks_config[task_id]
            
            # Thay thế biến động vào mô tả task
            description_template = task_cfg["description"]
            
            # Xây dựng bộ tham số định dạng an toàn
            format_kwargs = {
                "idea": idea,
                "previous_result": previous_result if previous_result else "",
                "script": "",
                "visual": "",
                "image": "",
                "voice": "",
                "video": ""
            }
            if all_results:
                for k, v in all_results.items():
                    format_kwargs[k] = v if v else ""
            
            formatted_description = description_template.format(**format_kwargs)
            
            # Khởi tạo Task
            task = Task(
                description=formatted_description,
                expected_output=task_cfg["expected_output"],
                agent=agent
            )
            
            # Thực thi tác vụ bằng agent
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            return f"❌ Lỗi stage {stage_name}: {str(e)}"

# Hàm bao (wrapper) để giữ tương thích ngược với luồng gọi cũ
def run_stage(stage_name: str, idea: str, previous_result: str = None, llm=None, all_results: dict = None, context: dict = None) -> str:
    engine = WorkflowEngine()
    return engine.run_stage(stage_name, idea, previous_result, llm, all_results, context)
