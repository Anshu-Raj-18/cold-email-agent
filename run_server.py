import uvicorn
from src.api_server import app

if __name__ == "__main__":
    print("Starting ColdMailer FastAPI Review Dashboard & REST Backend...")
    print("Visual Review Dashboard: http://localhost:8000/dashboard")
    print("Interactive API Docs    : http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
