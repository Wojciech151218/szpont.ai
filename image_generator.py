import base64
import uuid
from pathlib import Path

import requests
from langchain_core.runnables import RunnableLambda, RunnableParallel
from openai.types.images_response import ImagesResponse

from planner import ScenePlan
from models import image_generator_model


IMAGES_DIR = Path(__file__).resolve().parent / "images"


def _ensure_images_dir() -> Path:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    return IMAGES_DIR


def _save_image(response: ImagesResponse) -> str:
    """Save image from ImagesResponse to disk; return local file path."""
    _ensure_images_dir()
    if not response.data:
        raise ValueError("ImagesResponse has no image data")
    image = response.data[0]
    if image.url:
        img_data = requests.get(image.url).content
    elif image.b64_json:
        img_data = base64.b64decode(image.b64_json)
    else:
        raise ValueError("Image has neither url nor b64_json")
    filename = f"{uuid.uuid4().hex}.png"
    filepath = IMAGES_DIR / filename
    filepath.write_bytes(img_data)
    return str(filepath)


def _generate_images(prompts: list[str]) -> RunnableParallel:
    return RunnableParallel(
        **{
            f"img_{i}": RunnableLambda(lambda _, p=prompt: p)
            | image_generator_model
            | RunnableLambda(_save_image)
            for i, prompt in enumerate(prompts)
        }
    )

def _run(scene_plan: ScenePlan) -> dict:
    """Runnable entrypoint: build parallel image pipeline and invoke it."""
    runnable = _generate_images(scene_plan.prompts)
    return runnable.invoke({})


# Runnable Lambda: invoke with a prompt string or {"prompt": "..."}
image_generator_runnable = RunnableLambda(_run)

