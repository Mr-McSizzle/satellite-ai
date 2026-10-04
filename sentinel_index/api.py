"""
Offline Evaluation API for PS 26227.
Replaces the Gemini/cloud-based backend with local SQLite + FAISS retrieval.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from sentinel_index import config, search, change, db


engine_search: search.SearchEngine
engine_change: change.ChangeEngine

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine_search, engine_change
    db.init_db()
    engine_search = search.SearchEngine()
    engine_change = change.ChangeEngine()
    yield
    # Cleanup if needed

app = FastAPI(title="SatQuery Offline", lifespan=lifespan)

class TextQuery(BaseModel):
    query: str
    top_k: int = 20

@app.post("/api/v1/search/text")
def search_text(req: TextQuery):
    results = engine_search.text_search(req.query, req.top_k)
    return {"results": results}

@app.get("/api/v1/search/image")
def search_image(tile_id: str, top_k: int = 20):
    try:
        results = engine_search.image_search(tile_id, top_k)
        return {"results": results}
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.post("/api/v1/change/scan")
def scan_change():
    """Run full change detection across the indexed archive."""
    changes = engine_change.find_all_changes()
    
    # Insert candidates into review queue
    conn = db.get_connection()
    for c in changes:
        cand_id = f"cand_{c['evidence']['after_tile']}"
        conn.execute(
            "INSERT OR IGNORE INTO review_queue (candidate_id, type, tile_id, score) VALUES (?, ?, ?, ?)",
            (cand_id, "change", c["evidence"]["after_tile"], c["confidence"])
        )
    return {"found": len(changes), "changes": changes}

@app.get("/api/v1/review/queue")
def get_review_queue():
    conn = db.get_connection()
    rows = conn.execute("SELECT * FROM review_queue WHERE status = 'pending' ORDER BY score DESC LIMIT 50").fetchall()
    return {"queue": [dict(r) for r in rows]}

class ReviewDecision(BaseModel):
    candidate_id: str
    status: str
    note: str = ""

@app.post("/api/v1/review/decide")
def submit_review(req: ReviewDecision):
    if req.status not in ("confirmed", "rejected"):
        raise HTTPException(400, "status must be confirmed or rejected")
    
    conn = db.get_connection()
    conn.execute(
        "UPDATE review_queue SET status = ?, audit_note = ? WHERE candidate_id = ?",
        (req.status, req.note, req.candidate_id)
    )
    return {"status": "ok"}

@app.get("/api/v1/tiles/chip/{filename}")
def get_chip(filename: str):
    path = config.CHIPS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Chip not found")
    return FileResponse(path)
