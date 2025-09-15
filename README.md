# Backend Case API

A backend case study built with **FastAPI**, **Postgres (Neon)**, **SQLAlchemy**, and **Alembic**.  
It features JWT authentication, role-based access, and asynchronous note summarization.

---

## Features
- JWT-based signup & login  
- Roles: `ADMIN` (all notes), `AGENT` (own notes)  
- CRUD operations on notes with async summarization  
- Database migrations via Alembic (auto-run in entrypoint)  
- Dockerized & deployed on Render  

---

## Live Demo
Base URL: [https://proksiyazilim-backendcase.onrender.com](https://proksiyazilim-backendcase.onrender.com)  
Docs: [https://proksiyazilim-backendcase.onrender.com/docs](https://proksiyazilim-backendcase.onrender.com/docs)

---

## Explanation Video
Açıklama Videosu: [https://youtu.be/JVKJ_iByneI](https://youtu.be/JVKJ_iByneI)  

---

## Environment Variables

Create a `.env` file or configure these variables in your deployment platform:

```env
# App
ENV=prod
SECRET_KEY=supersecret123   # replace with a strong secret in production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database (Neon example)
DATABASE_URL=postgresql+psycopg://<USER>:<PASSWORD>@<HOST>/<DBNAME>?sslmode=require
```

## Quick Start (Local)
```bash
# Clone repo
git clone https://github.com/Betulyzc/ProksiYazilim-BackendCase
cd ProksiYazilim-BackendCase

# Run containers
docker compose up --build
