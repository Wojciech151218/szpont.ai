from langchain_core.runnables import RunnableLambda
from models import llm_model
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate,HumanMessagePromptTemplate
from planner.models import PlannerInput, PlannerOutput



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
