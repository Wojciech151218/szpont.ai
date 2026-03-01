import os

from pynamodb.attributes import JSONAttribute, ListAttribute, UnicodeAttribute
from pynamodb.models import Model
from pydantic import BaseModel, Field
from planner.models import PlannerHistory

class CreateSessionSchema(Model):
    history: JSONAttribute = JSONAttribute()
    id: str = UnicodeAttribute(hash_key=True)
    video_ids: list[str] = ListAttribute(default=list)
    image_ids: list[str] = ListAttribute(default=list)

    class Meta:
        table_name = os.getenv("DYNAMODB_CREATE_SESSION_TABLE", "create-session")
        region = os.getenv("AWS_REGION", "us-east-1")
        host = os.getenv("DYNAMODB_ENDPOINT_URL")


class CreateSessionModel(BaseModel):
    id: str = Field(description="The ID of the session")
    history: PlannerHistory = Field(description="The history of the conversation")
    video_ids: list[str] = Field(description="The IDs of the videos")
    image_ids: list[str] = Field(description="The IDs of the images")