from dotenv import load_dotenv
from fastapi import FastAPI

from create_session.create_session_handlers import router as create_session_router
from create_session.schemas import CreateSessionSchema
from planner.planner_handlers import router as planner_router
from image_generation.image_generation_handlers import router as image_generation_router
load_dotenv()

app = FastAPI(title="szpont.ai API")
app.include_router(create_session_router)
app.include_router(planner_router)
app.include_router(image_generation_router)


@app.on_event("startup")
def ensure_tables_exist() -> None:
    if not CreateSessionSchema.exists():
        CreateSessionSchema.create_table(
            read_capacity_units=1,
            write_capacity_units=1,
            wait=True,
        )
