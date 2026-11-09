import sqlite3
import json
from datetime import datetime
from app.core.config import DB_PATH
from app.services.seed_data import get_default_brand_kit

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Enable WAL mode for high performance
    cursor.execute("PRAGMA journal_mode=WAL;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brand_settings (
        id TEXT PRIMARY KEY,
        brand_data TEXT,
        updated_at TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS content_items (
        id TEXT PRIMARY KEY,
        title TEXT,
        content_type TEXT,
        current_status TEXT,
        original_content TEXT,
        current_content TEXT,
        score INTEGER,
        category_scores TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS findings (
        id TEXT PRIMARY KEY,
        item_id TEXT,
        category TEXT,
        severity TEXT,
        matched_text TEXT,
        start_char INTEGER,
        end_char INTEGER,
        explanation TEXT,
        rule_id TEXT,
        rule_name TEXT,
        citation_source TEXT,
        confidence_score INTEGER,
        fact_status TEXT,
        suggested_fix TEXT,
        FOREIGN KEY (item_id) REFERENCES content_items(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tracked_changes (
        id TEXT PRIMARY KEY,
        item_id TEXT,
        finding_id TEXT,
        original_text TEXT,
        replacement_text TEXT,
        start_char INTEGER,
        end_char INTEGER,
        status TEXT,
        rejection_reason TEXT,
        edited_text TEXT,
        FOREIGN KEY (item_id) REFERENCES content_items(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id TEXT PRIMARY KEY,
        item_id TEXT,
        author TEXT,
        role TEXT,
        comment_text TEXT,
        created_at TEXT,
        FOREIGN KEY (item_id) REFERENCES content_items(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        item_id TEXT,
        timestamp TEXT,
        actor TEXT,
        role TEXT,
        action TEXT,
        details TEXT,
        content_hash TEXT,
        FOREIGN KEY (item_id) REFERENCES content_items(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS content_versions (
        id TEXT PRIMARY KEY,
        item_id TEXT,
        version_number INTEGER,
        content TEXT,
        created_at TEXT,
        created_by TEXT,
        change_summary TEXT,
        score INTEGER,
        FOREIGN KEY (item_id) REFERENCES content_items(id) ON DELETE CASCADE
    );
    """)

    # Check if brand_settings is seeded
    cursor.execute("SELECT id FROM brand_settings WHERE id = 'default'")
    if not cursor.fetchone():
        default_kit = get_default_brand_kit()
        cursor.execute(
            "INSERT INTO brand_settings (id, brand_data, updated_at) VALUES (?, ?, ?)",
            ('default', json.dumps(default_kit.model_dump()), datetime.utcnow().isoformat())
        )

    conn.commit()
    conn.close()

