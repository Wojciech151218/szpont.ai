from langchain_core.runnables import RunnableLambda
from models import llm_model
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate,HumanMessagePromptTemplate
from planner.models import PlannerInput, PlannerOutput, ScenePlans



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
    


def _follow_up_message_template(input: PlannerInput) -> ChatPromptTemplate:
    messages = []
    for item in input.history.items:
        messages.append(item.user)
        messages.append(item.ai)

    
    return ChatPromptTemplate.from_messages([
        system_message,
        *messages,
        HumanMessagePromptTemplate.from_template(
        "edit the plan of the scenes: {plan} based on the user's request: {prompt}"
        )
    ])


initial_planner_pipeline = get_initial_prompt() | planner_model



def _plan_prettify(plan: ScenePlans) -> str:
    return "\n".join([f"{i+1}. {p}" for i, p in enumerate(plan.scenes)])

def _follow_up_to_messages(inp: PlannerInput):
    template = _follow_up_message_template(inp)
    return template.invoke({
        "plan": _plan_prettify(inp.current_plan) if inp.current_plan else "{}",
        "prompt": inp.prompt,
    })


follow_up_planner_pipeline = RunnableLambda(_follow_up_to_messages) | planner_model
