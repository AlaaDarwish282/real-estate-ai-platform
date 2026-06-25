import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.properties import router as properties_router
from api.licensing import router as licensing_router

app = FastAPI(
    title="Real Estate AI Platform",
    description="AI-powered property valuation, investment scoring, and license management",
    version="1.0.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(properties_router)
app.include_router(licensing_router)


@app.get("/")
def root():
    return {"service": "Real Estate AI Platform", "docs": "/docs", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=False)
