from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app =FastAPI(

    title= " F1 Race Prrdictor API",
    description = "Predict F1 race outcomes and simulate statergies",
    version ="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return{
        "message" : "F1 Race Predictor API",
        "Status" : "running",
        "version" : "0.1.0"

    }

@app.get("/health")
def health_check():
    return {
        "status" : "healthy"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host= "0.0.0.0" , port = 8000)