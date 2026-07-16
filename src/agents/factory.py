# MIT License
# Copyright (c) 2026 Manes2008/didicrew

import os
import yaml
from crewai import Agent
from src.tools.image_tool import generate_gpt_image

class AgentFactory:
    """
    Factory class để đọc cấu hình YAML và khởi tạo các CrewAI Agent.
    """
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join("config", "agents.yaml")
            
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def create_agent(self, agent_id: str, llm=None, context: dict = None) -> Agent:
        """
        Khởi tạo Agent dựa trên agent_id trong config.
        """
        if agent_id not in self.config:
            raise ValueError(f"Agent '{agent_id}' không tồn tại trong file cấu hình.")
            
        agent_cfg = self.config[agent_id]
        
        # Format lại text nếu có context
        from collections import defaultdict
        safe_context = defaultdict(str, context if context else {})
        
        role = agent_cfg["role"].format_map(safe_context)
        goal = agent_cfg["goal"].format_map(safe_context)
        backstory = agent_cfg["backstory"].format_map(safe_context)
        
        # Gán tool sinh ảnh nếu là Image Generation Specialist
        tools = []
        if agent_id == "image_generation_specialist":
            tools = [generate_gpt_image]
            
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=agent_cfg.get("verbose", False),
            max_iter=agent_cfg.get("max_iter", 10),
            allow_delegation=agent_cfg.get("allow_delegation", False),
            chat_llm=llm,
            tools=tools
        )
