from typing import Any
from uuid import uuid4

from pynamodb.exceptions import DoesNotExist

try:
    from .schemas import CreateSessionSchema
except ImportError:
    from schemas import CreateSessionSchema


class CreateSessionService:
    def create_session(
        self,
        history: list[dict[str, Any]] | None = None,
        video_ids: list[str] | None = None,
        image_ids: list[str] | None = None,
    ) -> CreateSessionSchema:
        session_id = str(uuid4())
        session = CreateSessionSchema(
            id=session_id,
            history=history or [],
            video_ids=video_ids or [],
            image_ids=image_ids or [],
        )
        session.save()
        return session

    def get_session(self, session_id: str) -> CreateSessionSchema | None:
        try:
            return CreateSessionSchema.get(session_id)
        except DoesNotExist:
            return None

    def add_videos(self, session_id: str, video_ids: list[str]) -> CreateSessionSchema:
        session = self._get_or_raise(session_id)
        self._extend_list_field(session, "video_ids", video_ids)
        return session

    def remove_videos(self, session_id: str, video_ids: list[str]) -> CreateSessionSchema:
        session = self._get_or_raise(session_id)
        self._remove_from_list_field(session, "video_ids", video_ids)
        return session

    def add_images(self, session_id: str, image_ids: list[str]) -> CreateSessionSchema:
        session = self._get_or_raise(session_id)
        self._extend_list_field(session, "image_ids", image_ids)
        return session

    def remove_images(self, session_id: str, image_ids: list[str]) -> CreateSessionSchema:
        session = self._get_or_raise(session_id)
        self._remove_from_list_field(session, "image_ids", image_ids)
        return session

    def update_history(self, session_id: str, history: list[dict[str, Any]]) -> CreateSessionSchema:
        session = self._get_or_raise(session_id)
        session.history = history
        session.save()
        return session

    def _get_or_raise(self, session_id: str) -> CreateSessionSchema:
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"Session '{session_id}' does not exist")
        return session

    def _extend_list_field(self, session: CreateSessionSchema, field_name: str, values: list[str]) -> None:
        if not values:
            return
        field_values = getattr(session, field_name)
        field_values.extend(values)
        session.save()

    def _remove_from_list_field(self, session: CreateSessionSchema, field_name: str, values: list[str]) -> None:
        field_values = getattr(session, field_name)
        if not field_values or not values:
            return
        to_remove = set(values)
        updated_values = [value for value in field_values if value not in to_remove]
        setattr(session, field_name, updated_values)
        session.save()
