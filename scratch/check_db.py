import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
sys.stdout.reconfigure(encoding='utf-8')

from src.core.models import get_db_session, Channel, Project, ChannelStageConfig

db = get_db_session()
try:
    print("--- CHANNELS ---")
    channels = db.query(Channel).all()
    for c in channels:
        print(f"Channel ID: {c.id} | Name: {c.name}")
        print(f"  Description: {c.description}")
        print(f"  Goal: {c.goal}")
        
        # In cấu hình AI các bước của kênh này
        configs = db.query(ChannelStageConfig).filter_by(channel_id=c.id).all()
        print("  AI Stages Configurations:")
        for cfg in configs:
            print(f"    Stage: {cfg.stage_name} | Role: {cfg.role}")
            print(f"      Goal: {cfg.goal}")
            print(f"      Backstory: {cfg.backstory[:100]}...")
            print(f"      Markdown Template: {cfg.markdown_template}")
finally:
    db.close()
