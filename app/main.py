from fastapi import FastAPI
from app.routes import users, notes
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Backend Case API", version="1.0")

# Router’ları ekle
app.include_router(users.router)
app.include_router(notes.router)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# ----------------- Custom OpenAPI (Swagger UI için) -----------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Backend Case API",
        version="1.0",
        description="Our case study API",
        routes=app.routes,
    )
    # Swagger UI için sadece Bearer Auth tanımı 
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # tüm endpointler için security zorunluluğu
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# FastAPI’nin varsayılan openapi fonksiyonunu override etmek için
app.openapi = custom_openapi
