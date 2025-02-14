# FileManager-API
-----Async File Manager-----

REST API for  download, save and contlor files. Example: storage docks, images.

## 🛠Stack:
- ✅ Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- ✅ Storage: MinIO (S3-storage)
- ✅ Extra: Celery

## Functional:
  - Autorizstion for cookies
  - Loadind, download, delete files
  - File metadata support
  - File versioning support

# How to start
```
git clone  https://github.com/PlatinumDCH/FileManager-API.git
```
```
cd FileManager-API
```
```
touch .env
```
```
fill data to envfile
```
```
docker-compose up -d
```
```
pip install poetry
```
```
poetry install
```
```
alembic -c alembic.ini upgrade head
```
```
fastapi dev backend/app/main.py
```

![alt text](frontend/static/img/cofe.jpg)


