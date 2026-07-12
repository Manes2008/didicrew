# test_gpt_image2.py
from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
import requests
from PIL import Image
from io import BytesIO

# Load API key từ file .env
load_dotenv()

print("=== TEST gpt-image-1-mini ===\n")

prompt = """A cute 3-year-old Vietnamese girl with fair skin, big eyes, 
bright pink twin pigtails, wearing a pink lace dress, dancing joyfully 
in Ghibli animation style, soft pastel colors, whimsical background"""

print(f"Prompt:\n{prompt}\n")
print("Đang tạo ảnh...")

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))   # Tự động lấy key từ .env

    response = client.images.generate(
        model="gpt-image-1-mini",
        prompt=prompt,
        size="1024x1024",
        quality="medium",
        n=1,
    )

    # 1. Lấy chuỗi mã hóa Base64 thay vì .url
    base64_data = response.data[0].b64_json

    if base64_data:
        print("\n✅ TẠO ẢNH THÀNH CÔNG (Đã nhận dữ liệu Base64)!")
        
        # 2. Giải mã Base64 thành dữ liệu nhị phân (bytes)
        img_bytes = base64.b64decode(base64_data)
        img = Image.open(BytesIO(img_bytes))

        # 3. Tải và lưu về máy
        os.makedirs("generated_images", exist_ok=True)
        filename = f"generated_images/test_{len(os.listdir('generated_images')) + 1}.png"
        img.save(filename)
        print(f"📁 Đã lưu file ảnh thành công tại: {filename}")

    else:
        print("\n❌ Không nhận được dữ liệu ảnh Base64 từ API.")

except Exception as e:
    print(f"\n❌ LỖI: {e}")