from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def homepage():
    return {'message' : 'hello from home pages'}