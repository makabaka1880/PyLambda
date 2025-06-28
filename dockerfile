# Use the official Python image
FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV DEFAULT_DB_PATH=/app/terms.db

CMD ["python", "/app/repl.py"]