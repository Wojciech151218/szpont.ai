from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class ScenePlans(BaseModel):
    scenes: list[str] = Field(description="The prompts to generate the scenes")


class PlannerOutput(BaseModel):
    plan: ScenePlans = Field(description="The plan of the video")
    response: str = Field(description="The response to the user")


class PlannerHistoryItem(BaseModel):
    plan: ScenePlans = Field(description="The plan of the video")
    user: HumanMessage = Field(description="The user's message")
    ai: AIMessage = Field(description="The AI's message")


class PlannerHistory(BaseModel):
    items: list[PlannerHistoryItem] = Field(description="The history of the conversation")

    def __add__(self, item: "PlannerHistoryItem") -> "PlannerHistory":
        new_history = self.items + [item]
        return PlannerHistory(
            plan=item.plan,
            user=item.user,
            ai=item.ai,
            items=new_history,
        )


class PlannerInput(BaseModel):
    n_scenes: int = Field(description="The number of scenes to generate")
    prompt: str = Field(description="The description of the video")
    history: PlannerHistory = Field(default=PlannerHistory(items=[]), description="The history of the conversation")
    current_plan: ScenePlans | None = Field(default=None, description="The current plan of the video")
