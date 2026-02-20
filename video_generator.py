from langchain.tools import StructuredTool
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class LumaInput(BaseModel):
    prompt: str

LUMA_API_KEY = os.getenv("LUMA_API_KEY")

def generate_luma_video(prompt: str):
    url = "https://api.lumalabs.ai/dream-machine/v1/generations"

    headers = {
        "Authorization": f"Bearer {LUMA_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "prompt": prompt,
        "aspect_ratio": "16:9"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data["id"]   # generation job id


luma_tool = StructuredTool.from_function(
    name="luma_video_generator",
    description="Creates cinematic AI videos using Luma Dream Machine",
    func=generate_luma_video,
    args_schema=LumaInput,
)





def get_generation_status(generation_id: str):
    url = f"https://api.lumalabs.ai/dream-machine/v1/generations/{generation_id}"

    headers = {
        "Authorization": f"Bearer {LUMA_API_KEY}"
    }

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    return r.json()