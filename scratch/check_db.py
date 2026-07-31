import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

# Set stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

from src.core.models import get_db_session, PromptOptimizationLog, Project

db = get_db_session()
try:
    print("--- LATEST PROJECTS ---")
    projects = db.query(Project).order_by(Project.id.desc()).limit(5).all()
    for p in projects:
        # Encode/decode to ignore encoding issues if reconfigure is not supported
        idea_str = p.idea[:50].encode('utf-8', errors='ignore').decode('utf-8')
        print(f"Project ID: {p.id}, Idea: {idea_str}, Stage: {p.current_stage}")

    print("\n--- LATEST PROMPT OPTIMIZATION LOGS ---")
    logs = db.query(PromptOptimizationLog).order_by(PromptOptimizationLog.id.desc()).limit(10).all()
    for l in logs:
        print(f"Log ID: {l.id}, Project ID: {l.project_id}, Step: {l.step_name}, Created: {l.created_at}")
finally:
    db.close()
