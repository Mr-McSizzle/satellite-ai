"""End-to-end smoke test for the GAIA unified backend (cloud chat + offline index)."""
import json
import sys
import time

import requests

BASE = "http://127.0.0.1:8000"
TIF = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\krish\satellite-ai\test1.tif"
TIF2 = sys.argv[2] if len(sys.argv) > 2 else r"c:\Users\krish\satellite-ai\test2.tif"


def step(name, fn):
    t = time.time()
    try:
        out = fn()
        print(f"[PASS] {name} ({time.time()-t:.1f}s) -> {out}")
        return out
    except Exception as e:
        print(f"[FAIL] {name} ({time.time()-t:.1f}s) -> {type(e).__name__}: {e}")
        return None


def upload(path, role):
    with open(path, "rb") as f:
        r = requests.post(f"{BASE}/api/v1/upload", files={"file": (path.split("\\")[-1], f, "image/tiff")},
                          data={"modality": "optical"}, timeout=120)
    r.raise_for_status()
    j = r.json()
    j["role"] = role
    return j


def analyze(body):
    r = requests.post(f"{BASE}/api/v1/analyze", json=body, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code}: {r.text[:400]}")
    return r.json()


step("health", lambda: requests.get(f"{BASE}/health", timeout=10).json())
u1 = step("upload before", lambda: upload(TIF, "before"))
u2 = step("upload after", lambda: upload(TIF2, "after"))

if u1:
    if u1.get("preview_url"):
        step("preview png", lambda: (lambda r: (r.status_code, r.headers.get("content-type"), len(r.content)))(
            requests.get(BASE + u1["preview_url"], timeout=20)))
    res = step("analyze single (vqa)", lambda: (lambda j: {"status": j["status"], "task": j["task"],
                                                           "answer": j["answer"][:160], "session": j.get("session_id")})(
        analyze({"query": "Describe what is visible in this image", "images": [
            {"reference": u1["reference"], "modality": "optical", "role": "before"}]})))
    if res and res.get("session"):
        step("analyze follow-up (session)", lambda: (lambda j: {"status": j["status"], "answer": j["answer"][:160]})(
            analyze({"query": "Are there any roads?", "session_id": res["session"]})))

if u1 and u2:
    step("analyze change (bi-temporal)", lambda: (lambda j: {"status": j["status"], "task": j["task"],
                                                             "answer": j["answer"][:160]})(
        analyze({"query": "What changed between before and after?", "images": [
            {"reference": u1["reference"], "modality": "optical", "role": "before"},
            {"reference": u2["reference"], "modality": "optical", "role": "after"}]})))

step("offline text search", lambda: len(requests.post(f"{BASE}/offline/api/v1/search/text",
                                                      json={"query": "urban buildings"}, timeout=60).json()["results"]))
step("offline change scan", lambda: requests.post(f"{BASE}/offline/api/v1/change/scan", timeout=60).json()["found"])
step("offline review queue", lambda: len(requests.get(f"{BASE}/offline/api/v1/review/queue", timeout=30).json()["queue"]))
step("frontend proxy /offline", lambda: requests.get("http://localhost:5173/offline/api/v1/review/queue", timeout=30).status_code)
step("frontend proxy /api", lambda: requests.get("http://localhost:5173/health", timeout=30).status_code)
