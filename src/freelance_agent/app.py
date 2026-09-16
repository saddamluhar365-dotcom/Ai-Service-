from fastapi import FastAPI

from freelance_agent.api.routes import router

app = FastAPI(title="Autonomous Freelance Agent", version="0.1.0")
app.include_router(router)
