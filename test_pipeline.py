import os
import json
import time
from fastapi.testclient import TestClient

from src.api_server import app
from src.database import init_db, seed_candidate_profile
from src.scraper import NATIONAL_FACULTY_CATALOG, INSTITUTE_FULL_NAMES

# 1. Initialize & Seed DB
init_db()
profile_path = os.path.join(os.path.dirname(__file__), "data", "candidate_profile.json")
with open(profile_path, "r", encoding="utf-8") as f:
    cand_data = json.load(f)
seed_candidate_profile(cand_data)

client = TestClient(app)

print("=== STEP 1: Candidate Verification ===")
res_cand = client.get("/api/candidate")
assert res_cand.status_code == 200
cand = res_cand.json()
print(f"Loaded Candidate: {cand['name']} ({cand['email']})")

print(f"\nTotal Pre-seeded Faculty in Catalog: {len(NATIONAL_FACULTY_CATALOG)}")
print(f"Total Institutes Mapped: {len(INSTITUTE_FULL_NAMES)}")

tiers = ["IIT", "IIIT", "IISc", "NIT", "IISER", "ISB", "IIM", "ALL"]
print("\n=== STEP 2: Multi-Tier Institute Discovery Verification ===")

for tier in tiers:
    res_tier = client.post("/api/professors/discover-and-rank", json={
        "institution_type": tier,
        "threshold": 70.0
    })
    assert res_tier.status_code == 200
    data = res_tier.json()
    print(f"[{tier:5}] -> Discovered: {data['total_discovered']:3d} | Shortlisted (>=70%): {data['shortlisted_count']:3d}")
    if data["professors"]:
        top = data["professors"][0]
        print(f"       Top Match: {top['name']} ({top['institution']} [{top['institution_type']}]) - {top['total_score']}% ({top['category']})")

print("\n=== STEP 3: Auto-Preparing ALL Shortlisted Application Packages ===")
t0 = time.time()
res_prep_all = client.post("/api/applications/prepare-all", json={
    "institution_type": "ALL",
    "threshold": 70.0
})
assert res_prep_all.status_code == 200
prep_all_data = res_prep_all.json()
print(f"[OK] {prep_all_data['message']} (Completed in {time.time() - t0:.2f}s)")

print("\n=== STEP 4: Simulating Human Approval & Dispatch for Top 2 Matches ===")
res_tracker = client.get("/api/applications/tracker")
assert res_tracker.status_code == 200
apps = res_tracker.json()["applications"]
print(f"Total Applications Ready in Tracker: {len(apps)}")

for app_item in apps[:2]:
    res_send = client.post("/api/application/send", json={
        "application_id": app_item["application_id"],
        "user_approved": True
    })
    assert res_send.status_code == 200
    print(f"[OK] Sent Application to {app_item['professor']} ({app_item['institution']}): Status {res_send.json()['application_status']}")

print("\n=== STEP 5: Verifying CSV Data Exports & Review Dashboard ===")
assert os.path.exists(os.path.join("data", "professors.csv"))
assert os.path.exists(os.path.join("data", "applications.csv"))
print(f"[OK] data/professors.csv exported successfully.")
print(f"[OK] data/applications.csv exported successfully.")

res_dash = client.get("/dashboard")
assert res_dash.status_code == 200
print(f"[OK] Review Dashboard Rendered Successfully ({len(res_dash.text)} bytes)")

print("\n[OK] ALL MULTI-TIER NATIONAL INSTITUTE TESTS PASSED WITH FULL AUTOMATION!")
