import os

from pynamodb.attributes import JSONAttribute, ListAttribute, UnicodeAttribute
from pynamodb.models import Model

class CreateSessionSchema(Model):
    history: JSONAttribute = JSONAttribute(description="The history of the conversation")
    id: str = UnicodeAttribute(hash_key=True, description="The id of the session")
    video_ids: list[str] = ListAttribute(description="The id of the video")
    image_ids: list[str] = ListAttribute(description="The id of the image")

    class Meta:
        table_name = os.getenv("DYNAMODB_CREATE_SESSION_TABLE", "create-session")
        region = os.getenv("AWS_REGION", "us-east-1")
        host = os.getenv("DYNAMODB_ENDPOINT_URL")