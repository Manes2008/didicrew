import requests
import json
import time

api_key = "pollo_mvVDIa2jcZBPW0whFy8tZf7Mj8m6ap5AFG9ySiTbNfce"
url = "https://pollo.ai/api/platform/generation/minimax/minimax-hailuo-02"

headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key
}

data = {
    "prompt": "A cinematic shot of a futuristic city"
}

# Maybe it needs input?
data2 = {
    "input": {
        "prompt": "A cinematic shot of a futuristic city"
    }
}

print("Gửi yêu cầu tạo video...")
response = requests.post(url, headers=headers, json=data)
if response.status_code == 400 and "input" in response.text:
    print("Thu lai voi input payload...")
    response = requests.post(url, headers=headers, json=data2)

print(f"Status Code: {response.status_code}")
try:
    resp_json = response.json()
    print(f"Response: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
    
    # Nếu có data và id, tiến hành poll
    if "data" in resp_json and "id" in resp_json["data"]:
        task_id = resp_json["data"]["id"]
        print(f"Task ID: {task_id}. Bắt đầu poll status...")
        poll_url = f"https://pollo.ai/api/platform/generation/tasks/{task_id}"
        
        for i in range(5):
            time.sleep(5)
            poll_resp = requests.get(poll_url, headers=headers)
            print(f"Poll {i+1} Status Code: {poll_resp.status_code}")
            try:
                print(f"Poll Response: {json.dumps(poll_resp.json(), indent=2, ensure_ascii=False)}")
                if poll_resp.json().get("data", {}).get("status") in ["success", "failed"]:
                    break
            except Exception as e:
                print(f"Lỗi parse JSON poll: {e}")
                print(poll_resp.text)
                break
except Exception as e:
    print(f"Lỗi parse JSON: {e}")
    print(response.text)
