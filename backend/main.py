from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.races import router as races_router
from api.drivers import router as drivers_router
from api.circuits import router as circuits_router
from api.stats import router as stats_router
from api.analytics import router as analytics_router
from api.predict import router as predict_router
import os
from dotenv import load_dotenv

load_dotenv()

app =FastAPI(

    title= " F1 Race Prrdictor API",
    description = "Comprehensive F1 data API with ML-powered predictions",
    version ="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(races_router)
app.include_router(drivers_router)
app.include_router(circuits_router)
app.include_router(stats_router)
app.include_router(analytics_router)
app.include_router(predict_router)

@app.get("/")
def read_root():
    return {
        "message": "F1 Race Predictor API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "races": "/api/races",
            "drivers": "/api/drivers",
            "circuits": "/api/circuits",
            "stats": "/api/stats",
            "analytics": "/api/analytics",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status" : "healthy",
        "database": os.getenv("DATABASE_URL", "Not configured").split("@")[-1] if os.getenv("DATABASE_URL") else "Not configured"
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(app, host= "0.0.0.0" , port = 8000)