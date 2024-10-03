FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m myuser && chown -R myuser:myuser /app
USER myuser

ENV PYTHONPATH=/app

CMD ["python", "-m", "triager"]
