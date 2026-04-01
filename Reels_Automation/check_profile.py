import json

def get_profiles():
    try:
        with open(r"C:\Users\USER\AppData\Local\Google\Chrome\User Data\Local State", "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in data["profile"]["info_cache"].items():
            print(f"Directory: {k} -> Name: {v.get('name')}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    get_profiles()
