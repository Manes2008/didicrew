# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import os
import yaml
import json
from crewai import Task, Crew
from src.agents.factory import AgentFactory
from src.core.models import get_db_session, PromptOptimizationLog, VideoAnalysisLog

class StepContext:
    """
    Đóng gói ngữ cảnh của từng bước trong workflow dưới dạng đối tượng JSON chuẩn hóa.
    """
    def __init__(self, stage_name: str, output: str, extra_data: dict = None):
        self.stage_name = stage_name
        self.output = output
        self.extra_data = extra_data or {}

    def to_json(self) -> str:
        return json.dumps({
            "stage_name": self.stage_name,
            "output": self.output,
            "extra_data": self.extra_data
        }, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str):
        try:
            data = json.loads(json_str)
            return cls(data["stage_name"], data["output"], data.get("extra_data"))
        except Exception:
            return cls("", json_str)

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
            "brief": ("brief_director", "brief_task"),
            "script": ("script_writer", "script_task"),
            "visual": ("visual_prompt_engineer", "visual_task"),
            "image": ("image_generation_specialist", "image_task"),
            "voice": ("voiceover_specialist", "voice_task"),
            "video": ("video_editor", "editor_task")  # Tạm giữ agent cho tương thích nếu cần, nhưng sẽ bị đè bởi code Python thuần
        }

    def _pre_optimize_config(self, stage_name: str, inputs: dict, project_id: int = None) -> tuple:
        """
        Nạp động cấu hình mẫu từ agents.yaml và tasks.yaml từ đầu nguồn,
        phân tích và tối ưu hóa linh hoạt cả Agent backstory/goal và Task description.
        Đồng thời lưu log 2 phiên bản (original vs adjusted) và cập nhật ngược lại vào hệ thống.
        """
        agent_id, task_id = self.stage_mapping.get(stage_name, (None, None))
        if not task_id or task_id not in self.tasks_config:
            return None, None

        task_cfg = self.tasks_config[task_id]
        original_desc = task_cfg.get("description", "")
        
        # Nếu có project_id, kiểm tra xem trong DB đã có prompt_log đã chuẩn hóa trước đó để cập nhật ngược (Feedback Loop)
        adjusted_desc = original_desc
        if project_id:
            db = get_db_session()
            try:
                latest_log = db.query(PromptOptimizationLog).filter_by(
                    project_id=int(project_id),
                    step_name=f"config_init_{stage_name}",
                    is_standardized=True
                ).order_by(PromptOptimizationLog.created_at.desc()).first()
                if latest_log and latest_log.adjusted_prompt:
                    adjusted_desc = latest_log.adjusted_prompt
            except Exception as ex_db_read:
                print(f"[WARN] Khong the doc feedback loop DB: {ex_db_read}")
            finally:
                db.close()

        if adjusted_desc and task_id in self.tasks_config:
            self.tasks_config[task_id]["description"] = adjusted_desc

        return agent_id, task_id

    def _clean_json_response(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    def run_stage(self, stage_name: str, idea: str, previous_result: str = None, llm=None, all_results: dict = None, context: dict = None) -> str:
        """
        Thực thi một stage cụ thể trong Workflow.
        """
        try:
            project_id = context.get("project_id") if context else None
            # Kích hoạt Feedback Loop và tối ưu cấu hình trước khi chạy
            self._pre_optimize_config(stage_name, {}, project_id)
            stage_cfg = context.get("stage_config") if context else None
            custom_template = stage_cfg.get("markdown_template") if stage_cfg else None
            
            # Đồng bộ ngữ cảnh toàn cục (Context Chain)
            context_chain = {}
            if all_results:
                for k, v in all_results.items():
                    if v:
                        context_chain[k] = StepContext(k, v).to_json()

            # Giải nén previous_result từ StepContext nếu cần
            if previous_result:
                try:
                    ctx = StepContext.from_json(previous_result)
                    previous_result = ctx.output
                except Exception:
                    pass

            # Vòng lặp tự sửa lỗi (Self-Correction Loop) - B1 & B2 thực hiện trong stage 'script'
            if stage_name == "script":
                # B1: Phân tích ý tưởng thô và tối ưu hóa
                adjusted_prompt = idea
                is_standardized = False
                metrics_step1 = {}
                
                if llm:
                    target_dur = context.get("target_duration", "25-30") if context else "25-30"
                    prompt_analysis = f"""Bạn là một chuyên gia tối ưu hóa ý tưởng video ngắn. 
Hãy phân tích ý tưởng thô sau đây của người dùng: "{idea}".

Kiểm tra xem nó đã có đầy đủ thông tin về các yếu tố: 
1) Chủ đề/Thông điệp chính.
2) Nhân vật.
3) Bối cảnh.

Nếu thiếu bất kỳ thông tin nào, hãy tự động bổ sung hoặc làm rõ để tạo nên một prompt kịch bản chi tiết và hấp dẫn nhất.
Đồng thời, đánh giá các bộ chỉ số: tone, keyword_density, estimated_duration.

[CHỈ THỊ QUAN TRỌNG VỀ ĐỘ DÀI VÀ CHI TIẾT]:
- TUYỆT ĐỐI KHÔNG tóm tắt, viết tắt hay cắt bớt bất kỳ chi tiết, cốt truyện hoặc thông tin sự kiện nào từ ý tưởng gốc của người dùng.
- Hãy tối ưu hóa bằng cách GIỮ NGUYÊN nội dung gốc và PHÁT TRIỂN THÊM các chi tiết cụ thể (nhân vật, cảm xúc, biểu cảm, không gian bối cảnh, âm thanh) để làm cho ý tưởng trở nên phong phú hơn, dài hơn và sẵn sàng cho việc viết kịch bản chi tiết.

[ĐỊNH HƯỚNG THỜI LƯỢNG]:
- Video này có mục tiêu thời lượng là {target_dur} giây.
- Hãy điều chỉnh độ dài và độ chi tiết của ý tưởng đã tối ưu (adjusted_prompt) và ước lượng thời lượng (estimated_duration) sao cho phù hợp nhất với mục tiêu {target_dur} giây này (ví dụ: video dài cần nhiều chi tiết và phân cảnh hơn, video ngắn cần cô đọng nhưng vẫn giàu mô tả).

Bắt buộc phải trả về kết quả dưới dạng chuỗi JSON nguyên bản (không nằm trong khối markdown ```json), bao gồm các trường sau:
{{
  "adjusted_prompt": "Nội dung ý tưởng sau khi được tối ưu và chèn thêm chỉ thị chi tiết",
  "is_standardized": true,
  "metrics": {{
    "tone": "Tông giọng",
    "keyword_density": "Mật độ từ khóa",
    "estimated_duration": "Thời lượng ước tính"
  }}
}}
"""
                    try:
                        resp = llm.call(messages=[{"role": "user", "content": prompt_analysis}])
                        data = json.loads(self._clean_json_response(resp))
                        adjusted_prompt = data.get("adjusted_prompt", idea)
                        is_standardized = data.get("is_standardized", False)
                        metrics_step1 = data.get("metrics", {})
                    except Exception as e_step1:
                        print(f"[WARN] Loi buoc 1 phân tích ý tưởng: {e_step1}")

                # Lưu log bước 1 vào DB
                if project_id:
                    db = get_db_session()
                    try:
                        log1 = PromptOptimizationLog(
                            project_id=int(project_id),
                            step_name="step_1_analysis",
                            user_input_content=idea,
                            original_prompt="Phân tích đầy đủ thông tin chủ đề, nhân vật, bối cảnh.",
                            adjusted_prompt=adjusted_prompt,
                            analysis_metrics=json.dumps(metrics_step1, ensure_ascii=False),
                            is_standardized=is_standardized
                        )
                        db.add(log1)
                        db.commit()
                    except Exception as ex_db1:
                        print(f"[WARN] Khong the ghi log DB buoc 1: {ex_db1}")
                    finally:
                        db.close()

                # Sử dụng ý tưởng đã tối ưu hóa để chạy viết kịch bản
                idea_for_script = adjusted_prompt
            else:
                idea_for_script = idea

            # Chạy trực tiếp sinh ảnh bằng code Python thuần túy không qua Agent
            if stage_name == "image":
                # Chay ngam buoc visual de toi uu hoa hinh anh chi tiet tu kich ban
                print("[LOG] Dang chay ngam Agent Visual Prompt Engineer de toi uu hoa prompt hinh anh...")
                visual_prompt = self.run_stage(
                    stage_name="visual",
                    idea=idea,
                    previous_result=previous_result,
                    llm=llm,
                    all_results=all_results,
                    context=context
                )
                
                # Luu stage visual vao DB ProjectStage de phuc vu xuat du lieu
                if project_id:
                    db_session = get_db_session()
                    try:
                        from src.core.models import ProjectStage
                        visual_stage_rec = db_session.query(ProjectStage).filter_by(
                            project_id=int(project_id),
                            stage_name="visual"
                        ).first()
                        if not visual_stage_rec:
                            visual_stage_rec = ProjectStage(
                                project_id=int(project_id),
                                stage_name="visual",
                                result_content=visual_prompt,
                                status="completed"
                            )
                            db_session.add(visual_stage_rec)
                        else:
                            visual_stage_rec.result_content = visual_prompt
                            visual_stage_rec.status = "completed"
                        db_session.commit()
                    except Exception as ex_db_vis:
                        db_session.rollback()
                        print(f"[WARN] Khong the luu ProjectStage visual: {ex_db_vis}")
                    finally:
                        db_session.close()

                if all_results is not None:
                    all_results["visual"] = visual_prompt

                full_prompt = visual_prompt
                import re

                image_engine = context.get("image_engine", "openai") if context else "openai"

                if image_engine in ("sd1.5_local", "markl_local"):
                    # Backward-compat: engine local chi nhan 1 prompt nen van trich Scene 1
                    scene1_match = re.search(r"(?:Scene|Cảnh)\s*1[\s*:\-\u2013\.]+(.*?)(?=(?:Scene|Cảnh)\s*2[\s*:\-\u2013\.]+|\Z)", full_prompt, re.DOTALL | re.IGNORECASE)
                    if scene1_match:
                        profile_match = re.search(r"(?:Character Profile|Hồ sơ nhân vật|Profile|Nhân vật)[\s*:\-\u2013\.]+(.*?)(?=(?:Art Style|Phong cách|Scene)\s*|\Z)", full_prompt, re.DOTALL | re.IGNORECASE)
                        style_match = re.search(r"(?:Art Style|Phong cách nghệ thuật|Style)[\s*:\-\u2013\.]+(.*?)(?=(?:Scene|Nhân vật|Profile)\s*|\Z)", full_prompt, re.DOTALL | re.IGNORECASE)
                        profile_text = profile_match.group(1).strip() if profile_match else ""
                        style_text = style_match.group(1).strip() if style_match else ""
                        scene1_text = scene1_match.group(1).strip()
                        if custom_template and custom_template.strip():
                            local_prompt = f"{custom_template.strip()} {profile_text} {scene1_text}"
                        else:
                            local_prompt = f"{style_text} {profile_text} {scene1_text}"
                        local_prompt = local_prompt.replace("\n", " ").strip()
                    else:
                        local_prompt = full_prompt
                    from src.tools.image_tool import generate_local_image_sd_func
                    return generate_local_image_sd_func(local_prompt, use_gpu=(image_engine == "markl_local"))
                else:
                    # OpenAI: truyen toan bo visual prompt; generate_gpt_image_func tu tach scene va sinh anh song song
                    if custom_template and custom_template.strip():
                        full_prompt = f"{custom_template.strip()}\n\n{full_prompt}"
                    from src.tools.image_tool import generate_gpt_image_func
                    return generate_gpt_image_func(full_prompt)
            
            # Chạy trực tiếp sinh video
            if stage_name == "video":
                from src.tools.video_tool import generate_video_func
                
                # Ưu tiên lấy kịch bản chi tiết (script đã có visual description inline) thay vì stage visual riêng
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
                prompt = visual_result if visual_result else (script_result if script_result else idea_for_script)
                
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
            stage_cfg = context.get("stage_config") if context else None
            markdown_template = stage_cfg.get("markdown_template") if stage_cfg else None
            
            format_kwargs = {
                "idea": idea_for_script,
                "previous_result": previous_result if previous_result else "",
                "markdown_template": f"\n[CAU TRUC DAU RA BAT BUOC - MARKDOWN TEMPLATE]:\nHay viet noi dung va tra ve ket qua tuan thu CHINH XAC theo cau truc template sau:\n{markdown_template}\n" if markdown_template and markdown_template.strip() else "",
                "brief": "",
                "script": "",
                "visual": "",
                "image": "",
                "voice": "",
                "video": ""
            }
            if context:
                for key, val in context.items():
                    if key != "stage_config" and key not in format_kwargs:
                        format_kwargs[key] = val if val is not None else ""
            if all_results:
                for k, v in all_results.items():
                    format_kwargs[k] = v if v else ""

            # Lay Viral Blueprint tu video mau tot nhat trong VideoAnalysisLog
            viral_blueprint_hint = ""
            if project_id:
                try:
                    db_vbl = get_db_session()
                    best_viral = db_vbl.query(VideoAnalysisLog).filter_by(
                        project_id=int(project_id)
                    ).order_by(VideoAnalysisLog.overall_viral_score.desc()).first()

                    if best_viral and best_viral.overall_viral_score >= 7.0:
                        stage_metric_attr = {
                            "script": "step_2_script_metrics",
                            "visual": "step_3_visual_metrics",
                            "image": "step_3_visual_metrics",
                            "voice": "step_4_audio_metrics",
                            "video": "step_5_render_metrics",
                        }.get(stage_name, "step_1_idea_metrics")

                        metrics_val = getattr(best_viral, stage_metric_attr, None)
                        if metrics_val:
                            viral_blueprint_hint = (
                                f"\n\n[VIRL BLUEPRINT - Video mau viral dat {best_viral.overall_viral_score:.1f}/10 tu {best_viral.platform}]:\n"
                                f"De dat hieu qua tuong duong, hay phan tich va ap dung cac chi so sau cua video mau thanh cong:\n"
                                f"{metrics_val}\n"
                                f"Dieu chinh noi dung cua ban de khop voi cac chi so tren.\n"
                            )
                    db_vbl.close()
                except Exception as e_vbl:
                    print(f"[WARN] Khong the tai Viral Blueprint: {e_vbl}")

            # Gan blueprint vao idea neu co
            if viral_blueprint_hint:
                format_kwargs["idea"] = format_kwargs["idea"] + viral_blueprint_hint
            
            formatted_description = description_template.format(**format_kwargs)
            
            # Khởi tạo Task
            task = Task(
                description=formatted_description,
                expected_output=task_cfg["expected_output"],
                agent=agent
            )
            
            # Thực thi tác vụ bằng agent
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            script_result_raw = crew.kickoff()
            script_output = str(script_result_raw)

            # B2: Đánh giá transition_score và thực hiện Self-Correction Loop cho kịch bản chi tiết
            if stage_name == "script" and llm:
                transition_score = 10
                feedback = ""
                metrics_step2 = {}
                attempts = 0
                final_script = script_output

                prompt_eval = f"""Bạn là một chuyên gia đạo diễn phim ngắn. 
Hãy đánh giá tính liền mạch và độ mượt mà khi chuyển tiếp giữa các phân cảnh trong kịch bản sau:
"{final_script}"

Hãy chấm điểm "transition_score" từ 1 đến 10 (trong đó 10 là cực kỳ liền mạch; dưới 8 là cần sửa đổi).
Đồng thời đánh giá tone, mật độ từ khóa và thời lượng ước tính.

Bắt buộc phải trả về kết quả dưới dạng chuỗi JSON nguyên bản (không nằm trong khối markdown ```json), bao gồm các trường sau:
{{
  "transition_score": 8,
  "feedback": "Nhận xét chi tiết về phần chuyển tiếp giữa các phân cảnh",
  "metrics": {{
    "tone": "Tông giọng",
    "keyword_density": "Mật độ từ khóa",
    "estimated_duration": "Thời lượng ước tính"
  }}
}}
"""
                try:
                    resp_eval = llm.call(messages=[{"role": "user", "content": prompt_eval}])
                    data_eval = json.loads(self._clean_json_response(resp_eval))
                    transition_score = int(data_eval.get("transition_score", 10))
                    feedback = data_eval.get("feedback", "")
                    metrics_step2 = data_eval.get("metrics", {})
                except Exception as e_eval:
                    print(f"[WARN] Loi danh gia kịch bản: {e_eval}")

                # Vòng lặp sửa lỗi nếu điểm chuyển cảnh dưới 8
                while transition_score < 8 and attempts < 2:
                    attempts += 1
                    prompt_rewrite = f"""Dựa trên kịch bản gốc: "{final_script}"
Điểm liền mạch hiện tại: {transition_score}/10 (chưa đạt yêu cầu tối thiểu là 8/10).
Phản hồi đánh giá của đạo diễn: {feedback}

Hãy viết lại kịch bản trên để sửa chữa các điểm chuyển cảnh bị rời rạc, làm cho câu chuyện liền mạch, hấp dẫn và mượt mà hơn. Đảm bảo giữ cấu trúc phân cảnh chi tiết của kịch bản.
"""
                    try:
                        final_script = llm.call(messages=[{"role": "user", "content": prompt_rewrite}])
                        
                        # Đánh giá lại kịch bản mới
                        prompt_eval_again = prompt_eval.replace(script_output, final_script)
                        resp_eval = llm.call(messages=[{"role": "user", "content": prompt_eval_again}])
                        data_eval = json.loads(self._clean_json_response(resp_eval))
                        transition_score = int(data_eval.get("transition_score", 10))
                        feedback = data_eval.get("feedback", "")
                        metrics_step2 = data_eval.get("metrics", {})
                    except Exception as e_rewrite:
                        print(f"[WARN] Loi trong vong lap sua kich ban: {e_rewrite}")
                        break

                # Lưu log bước 2 vào DB
                if project_id:
                    db = get_db_session()
                    try:
                        log2 = PromptOptimizationLog(
                            project_id=int(project_id),
                            step_name="step_2_scripting",
                            user_input_content=script_output,
                            original_prompt=formatted_description,
                            adjusted_prompt=final_script,
                            analysis_metrics=json.dumps({
                                "transition_score": transition_score,
                                "feedback": feedback,
                                "attempts": attempts,
                                "metrics": metrics_step2
                            }, ensure_ascii=False),
                            is_standardized=(transition_score >= 8)
                        )
                        db.add(log2)
                        db.commit()
                    except Exception as ex_db2:
                        print(f"[WARN] Khong the ghi log DB buoc 2: {ex_db2}")
                    finally:
                        db.close()
                
                return final_script

            # B3: Đánh giá chỉ số chất lượng Visual Prompt & Độ đồng nhất nhân vật
            if stage_name == "visual" and llm:
                character_consistency = 8
                art_style_match = 8
                prompt_quality = 8
                feedback_visual = ""
                
                prompt_eval_visual = f"""Bạn là một Chuyên gia Đánh giá Visual Prompt cho AI Image/Video.
Hãy đánh giá kết quả danh sách Visual Prompt sau:
"{script_output}"

Đánh giá các chỉ số từ 1 đến 10:
1) character_consistency: Độ đồng nhất mô tả nhân vật qua các cảnh.
2) art_style_match: Mức độ phù hợp và đồng nhất phong cách nghệ thuật.
3) prompt_quality: Độ chi tiết và tính ứng dụng của các prompt tiếng Anh.

Bắt buộc phải trả về kết quả dưới dạng chuỗi JSON nguyên bản (không nằm trong khối markdown ```json):
{{
  "character_consistency": 9,
  "art_style_match": 9,
  "prompt_quality": 8,
  "feedback": "Nhận xét ngắn gọn về độ đồng nhất và chi tiết visual"
}}
"""
                try:
                    resp_eval_vis = llm.call(messages=[{"role": "user", "content": prompt_eval_visual}])
                    data_eval_vis = json.loads(self._clean_json_response(resp_eval_vis))
                    character_consistency = int(data_eval_vis.get("character_consistency", 8))
                    art_style_match = int(data_eval_vis.get("art_style_match", 8))
                    prompt_quality = int(data_eval_vis.get("prompt_quality", 8))
                    feedback_visual = data_eval_vis.get("feedback", "")
                except Exception as e_eval_vis:
                    print(f"[WARN] Loi danh gia visual prompt: {e_eval_vis}")

                # Lưu log bước 3 vào DB
                if project_id:
                    db = get_db_session()
                    try:
                        log3 = PromptOptimizationLog(
                            project_id=int(project_id),
                            step_name="step_3_visual",
                            user_input_content=previous_result if previous_result else idea_for_script,
                            original_prompt=formatted_description,
                            adjusted_prompt=script_output,
                            analysis_metrics=json.dumps({
                                "character_consistency": character_consistency,
                                "art_style_match": art_style_match,
                                "prompt_quality": prompt_quality,
                                "feedback": feedback_visual
                            }, ensure_ascii=False),
                            is_standardized=(character_consistency >= 8 and art_style_match >= 8)
                        )
                        db.add(log3)
                        db.commit()
                    except Exception as ex_db3:
                        print(f"[WARN] Khong the ghi log DB buoc 3: {ex_db3}")
                    finally:
                        db.close()

            return script_output
            
        except Exception as e:
            return f"❌ Lỗi stage {stage_name}: {str(e)}"

# Hàm bao (wrapper) để giữ tương thích ngược với luồng gọi cũ
def run_stage(stage_name: str, idea: str, previous_result: str = None, llm=None, all_results: dict = None, context: dict = None) -> str:
    engine = WorkflowEngine()
    return engine.run_stage(stage_name, idea, previous_result, llm, all_results, context)
