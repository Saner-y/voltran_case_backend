import os
import httpx
import base64
from dotenv import load_dotenv

load_dotenv()

FAL_API_KEY = os.getenv("FAL_API_KEY")
FAL_API_URL = os.getenv("FAL_API_URL", "https://fal.run/fal-ai/bytedance/seedream/v4/edit")


async def generate_image_from_bytes(image_bytes: bytes, prompt_text: str):
    """
    Resim verisini Base64'e çevirir ve fal.ai'ye tek bir JSON payload'u içinde gönderir.
    """
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    data_url = f"data:image/png;base64,{base64_image}"

    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt_text,
        "image_urls": [data_url]
    }

    async with httpx.AsyncClient(timeout=300) as client:
        r = await client.post(FAL_API_URL, headers=headers, json=payload)
        print("🔹 Fal.ai status:", r.status_code)
        print("🔹 Fal.ai text:", r.text[:400])
        r.raise_for_status()
        return r.json()