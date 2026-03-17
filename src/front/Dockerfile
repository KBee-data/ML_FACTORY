FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install uv

COPY . .

RUN uv sync

CMD ["streamlit", "run", "src/front/streamlit_app.py", "--server.port=8501", "server-address=0.0.0.0"]