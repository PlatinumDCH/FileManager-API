# FileManager-API
-----Async File Manager-----

REST API for  download, save and contlor files. Example: storage docks, images and video.

## 🛠Stack:
- ✅ Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis
- ✅ Storage: MinIO (S3-storage)
- ✅ DevOps: Docker, Docker Compose, Nginx
- ✅ Extra: OAuth2, Celery

## Functional:
  - Autorizstion for JWT
  - Loadind, download, delete files
  - File metadata support
  - Access restriction (public/private files)
  - Generate temporary download links
  - File versioning support


![alt text](app/templates/static/cofe.jpg)

```FileManager-API/
├── app/
│   ├── api/                     # basic endpoint's
│   │   ├── v1/                  # version API
│   │   │   ├── endpoints/       # endopoint (files, users, ...)
│   │   │   ├── dependencies.py  # excemple, autentificatoion
│   │   │   └── routers.py       # rputes FastAPI
│   ├── core/                    # basic logic
│   │   ├── config.py            # configuration app
│   │   ├── security.py          # autentification and autorisation
│   │   └── celery.py            # configuration Celery
│   ├── db/                      # work with database
│   │   ├── models.py            # models SQLAlchemy
│   │   ├── schemas.py           # Pydantic schemas
│   │   └── crud.py              # CRUD opetations
│   ├── services/                # buicness logic
│   │   ├── file_service.py      # logic work with files
│   │   ├── user_service.py      # logic work with users
│   │   └── task_service.py      # logic bacraound tasks
│   ├── tasks/                   # async tasks Celery
│   │   ├── file_tasks.py        # task for work with files
│   │   └── user_tasks.py        # task for work with users
│   ├── utils/                   # helper functions
│   │   ├── file_utils.py        # units for file work
│   │   └── logging.py           # logging
│   └── main.py                  # pints start in app
├── tests/                       # tests
│   ├── unit/                    # unit-tests
│   └── integration/             # integrations tests
├── docker-compose.yml           # Docker Compose start server
├── Dockerfile                   # Dockerfile by FastAPI app
├── requirements.txt             # dependes Python
└── README.md                    # documentation project```
