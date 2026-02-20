import warnings

# Suppress Pydantic serialization warning from LangChain's with_structured_output:
# it stores the parsed Pydantic model in an internal 'parsed' field typed as None.
warnings.filterwarnings(
    "ignore",
    message=".*PydanticSerializationUnexpectedValue.*field_name=.parsed.",
    category=UserWarning,
)

from dotenv import load_dotenv

load_dotenv()

from main_pipeline import main_pipeline

if __name__ == "__main__":
    result = main_pipeline.invoke({
        "n_scenes": 3, 
        "description": "make a video about chengis khan and his adventures"
        })
