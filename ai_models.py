from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain_core.runnables import RunnableLambda


model_name = "gpt-4.1-mini"

llm_model = ChatOpenAI(model=model_name)

client = OpenAI()

image_generator_model = RunnableLambda(
    lambda prompt: client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )
)