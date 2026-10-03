FROM python:3.13-alpine
WORKDIR /app
RUN pip install --no-cache-dir fastapi==0.118.0 uvicorn==0.37.0
COPY app.py .
USER 65534:65534
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
