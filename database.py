import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

@contextmanager
def get_db_connection():
    """管理 DB 連線資源的上下文管理器"""
    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        yield conn 
    except Exception as e:
        print(f"🚨 [DB] 連線失敗：{e}")
        raise 
    finally:
        if conn:
            conn.close()

def record_flaw_to_db(conn, batch_id: int, file_path: str, description: str, severity: str):
    """執行 SQL 寫入與事務控制"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO flaw_records (batch_id, image_file_path, defect_description, severity)
                VALUES (%s, %s, %s, %s);
            """, (batch_id, file_path, description, severity))
        conn.commit() 
    except Exception as e:
        conn.rollback()
        raise e

