FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && mkdir -p /data && chown -R appuser:appuser /data

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
RUN chown -R appuser:appuser /app

EXPOSE 5000

ENV DB_PATH=/data/tasks.db
VOLUME /data

USER appuser

CMD ["python", "src/app.py"]
