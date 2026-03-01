from fastapi import HTTPException, status
from langchain_core.messages import AIMessage, HumanMessage

from planner.models import PlannerHistory, PlannerHistoryItem, PlannerInput
from planner.planner import initial_planner_pipeline, follow_up_planner_pipeline

class PlannerService:
    def __init__(self, initial_history: PlannerHistory | None) -> None:
        self._history = initial_history
        

    def plan(self, prompt: str, n_scenes: int) -> PlannerHistory:
        if self._history is None:
            result = initial_planner_pipeline.invoke({
                "n_scenes": n_scenes,
                "prompt": prompt,
            })
            new_history_item = PlannerHistoryItem(
                plan=result.plan,
                user=HumanMessage(content=prompt),
                ai=AIMessage(content=result.response),
            )
            return PlannerHistory(
                plan=new_history_item.plan,
                user=new_history_item.user,
                ai=new_history_item.ai,
                items=[new_history_item],
            )
        chat_history = PlannerHistory(
            plan=self._history.items[-1].plan,
            user=self._history.items[-1].user,
            ai=self._history.items[-1].ai,
            items=self._history.items,
        )
        planner_input = PlannerInput(
            current_plan=self._history.items[-1].plan,
            history=chat_history,
            prompt=prompt,
            n_scenes=n_scenes,
        )
        result = follow_up_planner_pipeline.invoke(planner_input)
        new_history_item = PlannerHistoryItem(
            plan=result.plan,
            user=HumanMessage(content=prompt),
            ai=AIMessage(content=result.response),
        )
        return self._history + new_history_item

    def _validate_history(self) -> None:
        if self._history is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="History is not initialized",
            )

    def _validate_history_length(self, n_steps: int) -> None:
        self._validate_history()
        if len(self._history.items) < n_steps:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                f"History has only {len(self._history.items)} steps, but {n_steps} steps are required"
                ),
            )

    def revert(self, n_steps: int) -> PlannerHistory:
        self._validate_history_length(n_steps)

        items = self._history.items[-n_steps:]
        last = items[-1]
        return PlannerHistory(plan=last.plan, user=last.user, ai=last.ai, items=items)

    def revert_edit(self, n_steps: int, prompt: str, n_scenes: int) -> PlannerHistory:
        self._validate_history_length(n_steps)
                
        items = self._history.items[-n_steps:]
        last = items[-1]
        new_history = PlannerHistory(plan=last.plan, user=last.user, ai=last.ai, items=items)
        return PlannerService(new_history).plan(prompt, n_scenes)
