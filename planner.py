from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableLambda
from models import llm_model
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate,HumanMessagePromptTemplate


class ScenePlan(BaseModel):
    prompts: list[str] = Field(description="The prompts to generate the scenes")

class PlannerOutput(BaseModel):
    plan: ScenePlan = Field(description="The plan of the video")
    response: str = Field(description="The response to the user")

class PlannerHistoryItem(BaseModel):
    plan: ScenePlan = Field(description="The plan of the video")
    user: HumanMessage = Field(description="The user's message")
    ai: AIMessage = Field(description="The AI's message")

class PlannerHistory(PlannerHistoryItem):
    history: list[PlannerHistoryItem] = Field(description="The history of the conversation")

    def __add__(self, item: "PlannerHistoryItem") -> "PlannerHistory":
        new_history = self.history + [item]
        return PlannerHistory(
            plan=item.plan,
            user=item.user,
            ai=item.ai,
            history=new_history,
        )


class PlannerInput(BaseModel):
    n_scenes: int = Field(description="The number of scenes to generate")
    prompt: str = Field(description="The description of the video")
    history: list[BaseMessage] | None = Field(default=None, description="The history of the conversation")
    plan: ScenePlan | None = Field(default=None, description="The of a scene of the video")



planner_model = llm_model.with_structured_output(PlannerOutput)


system_message = SystemMessage(
    content="You are a scene planner of a viral ai generated\
    short content video. You should design plans for each scene based on user requests and write a summary of your plan and ask users for confirmation or further details"
)

initial_human_message = HumanMessagePromptTemplate.from_template(
    "Create a {n_scenes} plans of scenes that will be used to create a viral ai generated\
    short content video. The scenes should be related to the following description: {prompt}"
)


def get_initial_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        system_message,
        initial_human_message
    ])
    


def follow_up_message(input: PlannerInput) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        system_message,
        *input.history,
        HumanMessagePromptTemplate.from_template(
        "edit the plan of the scene {plan} based on the user's request: {prompt}"
        )
    ])


initial_planner_pipeline = get_initial_prompt() | planner_model


def _follow_up_to_messages(inp: PlannerInput):
    template = follow_up_message(inp)
    return template.invoke({
        "plan": inp.plan.model_dump_json() if inp.plan else "{}",
        "prompt": inp.prompt,
    })


follow_up_planner_pipeline = RunnableLambda(_follow_up_to_messages) | planner_model


def plan(history: PlannerHistory | None, prompt: str, n_scenes: int) -> PlannerHistory:
    if history is None:
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
            history=[new_history_item],
        )
    else:
        chat_history = []
        for item in history.history:
            chat_history.append(item.user)
            chat_history.append(item.ai)
        input = PlannerInput(plan=history.history[-1].plan, history=chat_history, prompt=prompt, n_scenes=n_scenes)
        result = follow_up_planner_pipeline.invoke(input)
        new_history_item = PlannerHistoryItem(
            plan=result.plan,
            user=HumanMessage(content=prompt),
            ai=AIMessage(content=result.response),
        )
        return history + new_history_item

def plan_revert(history: PlannerHistory, n_steps: int) -> PlannerHistory:
    if len(history.history) < n_steps:
        raise ValueError(f"History has only {len(history.history)} steps, but {n_steps} steps are required")
    items = history.history[-n_steps:]
    last = items[-1]
    return PlannerHistory(plan=last.plan, user=last.user, ai=last.ai, history=items)

def plan_revert_edit(history: PlannerHistory, n_steps: int, prompt: str, n_scenes: int) -> PlannerHistory:
    if len(history.history) < n_steps:
        raise ValueError(f"History has only {len(history.history)} steps, but {n_steps} steps are required")
    items = history.history[-n_steps:]
    last = items[-1]
    new_history = PlannerHistory(plan=last.plan, user=last.user, ai=last.ai, history=items)
    return plan(new_history, prompt, n_scenes)

