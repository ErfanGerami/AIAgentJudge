FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN pip install redis docker 


COPY . .

RUN ls -la /app/


CMD ["sleep", "infinity"]
# CMD ["python3","/app/worker.py"]