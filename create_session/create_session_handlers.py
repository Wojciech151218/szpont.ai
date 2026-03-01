from typing import Any

from fastapi import APIRouter, HTTPException, status

try:
    from .create_session_service import CreateSessionService
except ImportError:
    from create_session_service import CreateSessionService


router = APIRouter(prefix="/create-session", tags=["create-session"])
create_session_service = CreateSessionService()




@router.get("/{session_id}")
def get_create_session(session_id: str) -> dict[str, Any]:
    session = create_session_service.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' does not exist",
        )
    return session.attribute_values
