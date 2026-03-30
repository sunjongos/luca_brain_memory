import json

with open("cafe_reputation_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

negative_keywords = ["불친절", "최악", "가지마", "별로", "비추", "오진", "부작용", "짜증", "싸가지", "대충"]
namyangju_keywords = ["남양주", "장현", "오남", "진접"]

filtered_results = []

for query, items in data.items():
    for item in items:
        text = item["title"] + " " + item["description"]
        
        # Must mention '백병원' and some regional keyword indicating it's the Namyangju branch
        # (or just "남양주 백병원" explicitly)
        is_namyangju = "남양주" in text or "장현" in text or "진접" in text or "남양주 백병원" in text or "남양주백병원" in text
        
        if is_namyangju and "백병원" in text:
            # Check for negative sentiments
            # If the query itself was a negative query, include it, or check text
            is_negative = any(nk in text.replace(" ", "") for nk in negative_keywords)
            
            if is_negative:
                # To avoid duplicates
                if not any(r["link"] == item["link"] for r in filtered_results):
                    filtered_results.append(item)

print(f"Found {len(filtered_results)} potential negative reviews for Namyangju Paik Hospital:")
for idx, res in enumerate(filtered_results, 1):
    print(f"\n[{idx}] {res['title']}")
    print(f"Cafe: {res['cafename']}")
    print(f"Link: {res['link']}")
    print(f"Desc: {res['description']}")

with open("filtered_negative_reviews.json", "w", encoding="utf-8") as f:
    json.dump(filtered_results, f, ensure_ascii=False, indent=2)
