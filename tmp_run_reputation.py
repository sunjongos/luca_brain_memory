import sys
import os
import json
from pathlib import Path

# Add the skill directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / ".agent" / "skills" / "naver_search_trend"))
from naver_api import search_naver

queries = [
    "남양주 백병원", 
    "백병원 불친절", 
    "백병원 별로", 
    "백병원 최악", 
    "남양주 백병원 가지마세요",
    "남양주 백병원 비추"
]

results_dict = {}

for q in queries:
    print(f"Searching for: {q}")
    res = search_naver(q, target="cafearticle", display=50)
    if res and "items" in res:
        results_dict[q] = res["items"]
    else:
        results_dict[q] = []

with open("cafe_reputation_results.json", "w", encoding="utf-8") as f:
    json.dump(results_dict, f, ensure_ascii=False, indent=2)
print("Saved to cafe_reputation_results.json")
