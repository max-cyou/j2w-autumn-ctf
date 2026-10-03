FROM python:3.13-alpine
WORKDIR /app
RUN pip install --no-cache-dir Flask==3.1.2
COPY app.py .
USER 65534:65534
CMD ["python", "app.py"]
