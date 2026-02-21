from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableLambda
from models import llm_model
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate,HumanMessagePromptTemplate

class ScenePlan(BaseModel):
    prompts: list[str] = Field(description="The prompts to generate the scenes")

class PlannerOutput(BaseModel):
    plan: ScenePlan = Field(description="The plan of the video")
    response: str = Field(description="The response to the user")

class PlannerResponse(PlannerOutput):
    history: list[BaseMessage] = Field(description="The history of the conversation")


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


def plan(input: PlannerInput) -> PlannerResponse:
    if input.plan is None or input.history is None:
        response = initial_planner_pipeline.invoke({
            "n_scenes": input.n_scenes,
            "prompt": input.prompt,
        })
    else:
        response = follow_up_planner_pipeline.invoke(input)

    return PlannerResponse(**response.model_dump(), history=input.history)