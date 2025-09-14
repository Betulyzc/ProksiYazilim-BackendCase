set -e

echo " Alembic migration çalıştırılıyor..."
alembic upgrade head

echo " Migration bitti, Uvicorn başlatılıyor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000