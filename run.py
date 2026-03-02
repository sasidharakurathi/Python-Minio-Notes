import uvicorn

if __name__ == "__main__":
    # "main:app" refers to the 'app' instance inside 'main.py'
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Makes the server accessible on your local network
        port=8000,       # The port the server will listen on
        reload=True      # Enables auto-reloading when you change the code (great for dev)
    )