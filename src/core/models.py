import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, BigInteger, ForeignKey, UniqueConstraint, Boolean, LargeBinary, Float, Numeric
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, validates
import sys
import os
# Đảm bảo root directory có trong sys.path để import config.py
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import config
DATABASE_URL = config.DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db_session():
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Người dùng đóng thủ công hoặc qua try/finally ở nơi gọi

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    goal = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    configs = relationship("ChannelStageConfig", back_populates="channel", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="channel", cascade="all, delete-orphan")

    @validates("name")
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("Tên kênh không được để trống")
        if len(name) > 50:
            raise ValueError("Tên kênh không được vượt quá 50 ký tự")
        return name.strip()

    @validates("goal")
    def validate_goal(self, key, goal):
        if not goal or not goal.strip():
            raise ValueError("Mục tiêu của kênh không được để trống")
        return goal.strip()


class ChannelStageConfig(Base):
    __tablename__ = "channel_stage_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    stage_name = Column(String(20), nullable=False)
    role = Column(String(255), nullable=False)
    goal = Column(Text, nullable=False)
    backstory = Column(Text, nullable=False)
    markdown_template = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("channel_id", "stage_name", name="uq_channel_stage"),
    )

    channel = relationship("Channel", back_populates="configs")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    idea = Column(Text, nullable=False)
    provider = Column(String(50), nullable=False)
    model_name = Column(String(50), nullable=False)
    current_stage = Column(String(20), default="script")
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    channel = relationship("Channel", back_populates="projects")
    stages = relationship("ProjectStage", back_populates="project", cascade="all, delete-orphan")
    duration_config = relationship("VideoDurationConfig", uselist=False, back_populates="project", cascade="all, delete-orphan")
    prompt_logs = relationship("PromptOptimizationLog", back_populates="project", cascade="all, delete-orphan")
    video_analysis_logs = relationship("VideoAnalysisLog", back_populates="project", cascade="all, delete-orphan")

    @validates("idea")
    def validate_idea(self, key, idea):
        if not idea or not idea.strip():
            raise ValueError("Ý tưởng video không được để trống")
        if len(idea.strip()) < 5:
            raise ValueError("Ý tưởng video quá ngắn (tối thiểu 5 ký tự)")
        return idea.strip()


class ProjectStage(Base):
    __tablename__ = "project_stages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    stage_name = Column(String(20), nullable=False)
    result_content = Column(Text, nullable=True)
    media_path = Column(String(255), nullable=True)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("project_id", "stage_name", name="uq_project_stage"),
    )

    project = relationship("Project", back_populates="stages")
    media_files = relationship("MediaFile", back_populates="project_stage", cascade="all, delete-orphan")


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_stage_id = Column(Integer, ForeignKey("project_stages.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    status = Column(String(20), default="active")
    file_data = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project_stage = relationship("ProjectStage", back_populates="media_files")


class AllowedIP(Base):
    __tablename__ = "allowed_ips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(45), unique=True, nullable=False)
    label = Column(String(100), nullable=True)  # Ten thiet bi hoac ghi chu
    status = Column(String(20), default="pending", nullable=False)  # pending/approved/rejected
    is_admin_ip = Column(Boolean, default=False, nullable=False)  # IP duoc phep vao admin panel
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="allowed_ips")

    @validates("ip_address")
    def validate_ip(self, key, ip):
        import re
        if not ip or not ip.strip():
            raise ValueError("Địa chỉ IP không được để trống")
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$|^([0-9a-fA-F:]+)$'
        if not re.match(pattern, ip.strip()):
            raise ValueError(f"Địa chỉ IP không hợp lệ: {ip}")
        return ip.strip()

    @validates("status")
    def validate_status(self, key, status):
        allowed = {"pending", "approved", "rejected"}
        if status not in allowed:
            raise ValueError(f"Trạng thái phải là một trong: {allowed}")
        return status


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # user/admin
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    allowed_ips = relationship("AllowedIP", back_populates="user", cascade="all, delete-orphan")

    @validates("username")
    def validate_username(self, key, username):
        if not username or not username.strip():
            raise ValueError("Tên đăng nhập không được để trống")
        if len(username.strip()) < 3:
            raise ValueError("Tên đăng nhập phải có ít nhất 3 ký tự")

        return username.strip().lower()


class VideoDurationConfig(Base):
    __tablename__ = "video_duration_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    duration_type = Column(String(20), nullable=False)  # system_generated, uploaded_video
    target_duration = Column(Integer, default=0)
    min_duration = Column(Integer, default=0)
    max_duration = Column(Integer, default=0)
    video_source_id = Column(String(100), nullable=True)
    video_source_path = Column(Text, nullable=True)
    system_ratio_multiplier = Column(Numeric(3, 2), default=1.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="duration_config")


class PromptOptimizationLog(Base):
    __tablename__ = "prompt_optimization_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    step_name = Column(String(30), nullable=False)  # step_1_analysis, step_2_scripting
    user_input_content = Column(Text, nullable=False)
    original_prompt = Column(Text, nullable=False)
    adjusted_prompt = Column(Text, nullable=False)
    analysis_metrics = Column(Text, nullable=True)  # Chuoi JSON text
    is_standardized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="prompt_logs")


class VideoAnalysisLog(Base):
    __tablename__ = "video_analysis_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    video_url = Column(Text, nullable=False)
    platform = Column(String(20), nullable=False)  # youtube, tiktok
    step_1_idea_metrics = Column(Text, nullable=True)  # JSON text
    step_2_script_metrics = Column(Text, nullable=True)  # JSON text
    step_3_visual_metrics = Column(Text, nullable=True)  # JSON text
    step_4_audio_metrics = Column(Text, nullable=True)  # JSON text
    step_5_render_metrics = Column(Text, nullable=True)  # JSON text
    overall_viral_score = Column(Float, default=0.0)
    analysis_report = Column(Text, nullable=False)  # Markdown text
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="video_analysis_logs")


class SystemConfig(Base):
    """Bảng lưu cấu hình hệ thống persistent (API keys mã hóa, v.v.)"""
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)  # Giá trị đã mã hóa (Fernet)
    is_encrypted = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
