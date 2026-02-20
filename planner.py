from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from models import llm_model

class ScenePlan(BaseModel):
    prompts: list[str] = Field(description="The prompts to generate the scenes")


planner_model = llm_model.with_structured_output(ScenePlan)

planner_prompt = PromptTemplate(
    template="Create a {n_scenes} plans of scenes that will be used to create a viral ai generated\
    short content video. The scenes should be related to the following description: {description}",
    input_variables=["n_scenes", "description"]
)