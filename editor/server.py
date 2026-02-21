"""PocketStory World Editor — FastAPI backend.

Run from project root:
    uvicorn editor.server:app --reload --port 8787

Then open: http://localhost:8787
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import json

WORLDS_DIR = Path(__file__).parent.parent / "worlds"
EDITOR_DIR = Path(__file__).parent

app = FastAPI(title="PocketStory World Editor")

# Serve static editor files
app.mount("/static", StaticFiles(directory=str(EDITOR_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(EDITOR_DIR / "index.html")


@app.get("/worlds")
def list_worlds():
    """Return sorted list of world names (without .json extension)."""
    names = sorted(p.stem for p in WORLDS_DIR.glob("*.json"))
    return names


@app.get("/worlds/{name}")
def get_world(name: str):
    path = WORLDS_DIR / f"{name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"World '{name}' not found")
    return JSONResponse(content=json.loads(path.read_text(encoding="utf-8")))


@app.put("/worlds/{name}")
async def save_world(name: str, request_body: dict):
    path = WORLDS_DIR / f"{name}.json"
    path.write_text(
        json.dumps(request_body, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"saved": name}
