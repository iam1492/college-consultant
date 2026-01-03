dev-backend:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:
	npm --prefix nextjs run dev

adk-web:
	uv run adk web