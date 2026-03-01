from image_generation.image_generation_service import ImageGenerationService
from bucket.bucket_service import BucketService
from fastapi import APIRouter
from create_session.create_session_service import CreateSessionService
from pydantic import BaseModel
from create_session.schemas import CreateSessionSchema
from create_session.schemas import CreateSessionModel

router = APIRouter(prefix="/image-generation", tags=["image-generation"])
image_generation_service = ImageGenerationService(
    save_method=BucketService().save_image_from_image_response
    )
create_session_service = CreateSessionService()






@router.post("/{session_id}")
def generate_images(session_id: str) -> CreateSessionModel:
    scene_plan = create_session_service.get_scene_plan(session_id)
    image_ids = image_generation_service.generate_images(scene_plan)
    return create_session_service.update_images(session_id, image_ids)

@router.delete("/{session_id}")
def delete_images(session_id: str) -> CreateSessionModel:
    return create_session_service.update_images(session_id, [])
