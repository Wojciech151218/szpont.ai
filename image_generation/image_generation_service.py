from bucket.bucket_service import BucketService
from planner.models import ScenePlans
from image_generation.image_generation import image_generator_runnable
from openai.types.images_response import ImagesResponse
from create_session.create_session_service import CreateSessionService
from typing import Callable

class ImageGenerationService:
    def __init__(self, save_method: Callable[[ImagesResponse], str]):
       self.save_method = save_method
    def generate_image(self, scene_plans: ScenePlans):
        image_ids = []

        def _save_method(image_response: ImagesResponse):
            file_id = self.save_method(image_response)
            image_ids.append(file_id)


        image_generator_runnable(
            scene_plans=scene_plans,
            save_method=_save_method
        ).invoke()

        return image_ids