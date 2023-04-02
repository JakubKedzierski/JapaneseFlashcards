FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]