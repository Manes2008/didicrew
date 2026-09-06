import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
from src.core.models import get_db_session, ProjectStage

db = get_db_session()
stages = db.query(ProjectStage).order_by(ProjectStage.id.desc()).limit(4).all()
for s in reversed(stages):
    content = s.result_content or ""
    print(f"==================================================")
    print(f"STAGE: {s.stage_name} | Length: {len(content)} characters")
    print(f"==================================================")
    print(content)
    print("\n")
