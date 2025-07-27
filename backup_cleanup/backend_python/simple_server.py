from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting server on port 8080...")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info") 