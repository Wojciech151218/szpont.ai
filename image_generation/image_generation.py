import base64
import uuid
from pathlib import Path

import requests
from langchain_core.runnables import RunnableLambda, RunnableParallel
from openai.types.images_response import ImagesResponse

from planner.models import ScenePlans
from ai_models import image_generator_model
from typing import Callable




def image_generator_runnable(scene_plans: ScenePlans,save_method: Callable[[ImagesResponse], None]) -> RunnableParallel:
    """Runnable entrypoint: build parallel image pipeline and invoke it."""
    return RunnableParallel(
        **{
            f"img_{i}": RunnableLambda(lambda _, p=prompt: p)
            | image_generator_model
            | RunnableLambda(save_method)
            for i, prompt in enumerate(scene_plans.scenes)
        }
    )
    




