from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


from app.config.database import get_conn_db

app = FastAPI()

@app.get('/')
async def homepage():
    return {'message' : 'hello from home pages'}

@app.get("/check")
async def connect_verify(db: AsyncSession = Depends(get_conn_db)):     
    try:
        result = (await db.execute(text("SELECT 1"))).fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, 
                detail="Database is not configured correctly"
            )
        return {"message": "Database is working correctly"}
    except Exception:
        raise HTTPException(
            status_code=500, 
            detail="Error connecting to the database"
        )