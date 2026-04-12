from fastapi import FastAPI

app = FastAPI(
    title="TaskFlow",
    version="0.1.0",
    description="Aplicação web local para gerenciamento de tarefas colaborativas"
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}