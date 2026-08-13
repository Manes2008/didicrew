import os
import sys

sys.path.append(os.getcwd())

from src.core.models import get_db_session
from sqlalchemy import text

db = get_db_session()
sql = """
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT table_name, column_name, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND column_default LIKE 'nextval(%'
    LOOP
        EXECUTE 'SELECT setval(''' || 
                pg_get_serial_sequence(r.table_name, r.column_name) || 
                ''', COALESCE((SELECT MAX(' || quote_ident(r.column_name) || ') FROM ' || quote_ident(r.table_name) || '), 1));';
    END LOOP;
END $$;
"""
try:
    db.execute(text(sql))
    db.commit()
    print("SUCCESS: Reset all database sequences successfully!")
except Exception as e:
    db.rollback()
    print(f"FAILED to reset database sequences: {e}")
finally:
    db.close()
