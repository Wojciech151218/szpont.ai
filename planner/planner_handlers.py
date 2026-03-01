from typing import Any

from pydantic_core import ValidationError

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from planner.models import PlannerHistory, PlannerHistoryItem
from planner.planner_service import PlannerService 
from pydantic_core import ValidationError

try:
    from create_session.create_session_service import CreateSessionService
except ImportError:
    from ..create_session.create_session_service import CreateSessionService


router = APIRouter(prefix="/planner", tags=["planner"])
create_session_service = CreateSessionService()


class PlanRequest(BaseModel):
    prompt: str = Field(description="User prompt for planning")
    n_scenes: int = Field(description="Target number of scenes")


class RevertRequest(BaseModel):
    n_steps: int = Field(description="How many history steps to keep")


class RevertEditRequest(BaseModel):
    n_steps: int = Field(description="How many history steps to keep before editing")
    prompt: str = Field(description="Prompt for the follow-up edit")
    n_scenes: int = Field(description="Target number of scenes")


class PlannerSessionResponse(BaseModel):
    session_id: str
    history: PlannerHistory




def _history_from_payload(payload: list[dict[str, Any]] | None) -> PlannerHistory | None:
    if not payload:
        return None
    try:
        history = PlannerHistory.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored session history has invalid format",
        ) from exc
    return history


def _load_session_history_or_404(session_id: str) -> PlannerHistory | None:
    session = create_session_service.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' does not exist",
        )
    return _history_from_payload(session.history)


def _persist_history(session_id: str, history: PlannerHistory) -> None:
    try:
        create_session_service.update_history(session_id,history)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("")
def create_plan(body: PlanRequest) -> PlannerSessionResponse:
    history = PlannerService(None).plan(body.prompt, body.n_scenes)
    session = create_session_service.create_session(history=history.model_dump())
    return PlannerSessionResponse(session_id=session.id, history=history)


@router.post("/{session_id}")
def update_plan(session_id: str, body: PlanRequest) -> PlannerSessionResponse:
    history = _load_session_history_or_404(session_id)
    next_history = PlannerService(history).plan(body.prompt, body.n_scenes)
    _persist_history(session_id, next_history)
    return PlannerSessionResponse(session_id=session_id, history=next_history)


@router.patch("/{session_id}/revert")
def revert_plan(session_id: str, body: RevertRequest) -> PlannerSessionResponse:
    history = _load_session_history_or_404(session_id)
    next_history = PlannerService(history).revert(body.n_steps)
    _persist_history(session_id, next_history)
    return PlannerSessionResponse(session_id=session_id, history=next_history)


@router.patch("/{session_id}/revert-edit")
def revert_edit_plan(session_id: str, body: RevertEditRequest) -> PlannerSessionResponse:
    history = _load_session_history_or_404(session_id)
    next_history = PlannerService(history).revert_edit(body.n_steps, body.prompt, body.n_scenes)
    _persist_history(session_id, next_history)
    return PlannerSessionResponse(session_id=session_id, history=next_history)
