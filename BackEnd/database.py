# db.py
import json
import aiosqlite
from typing import List, Tuple
import cv2
import mediapipe as mp

DB_PATH = "storage.db"

#track photos and pciture from users
CREATE_SQL = """ 
CREATE TABLE IF NOT EXISTS embeddings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  person_id TEXT NOT NULL,
  embedding TEXT NOT NULL,       -- JSON array of floats
  quality REAL NOT NULL DEFAULT 0.0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_person_id ON embeddings(person_id);
"""

async def init_db(): 
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_SQL)
        await db.commit()

async def insert_embedding(person_id: str, embedding: List[float], quality: float = 0.0): #"this is fof imprbedding the pic and to the system"/
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO embeddings (person_id, embedding, quality) VALUES (?, ?, ?)",
            (person_id, json.dumps(embedding), float(quality)),
        )
        await db.commit()

async def fetch_all_embeddings() -> List[Tuple[str, List[float], float]]: #grabs the picture of ppl when needed
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT person_id, embedding, quality FROM embeddings")
        rows = await cur.fetchall()

    out = []
    for person_id, emb_json, quality in rows: #converts the json back to list
        out.append((person_id, json.loads(emb_json), float(quality)))
    return out


