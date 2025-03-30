# Use the official Python image
FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# TODO: Create server
# EXPOSE 5000

VOLUME ["/app/data"]

RUN echo "DEFAULT_DB_PATH=\"/app/data/terms.db\"" >> /app/.env

CMD ["python", "/app/repl.py"]