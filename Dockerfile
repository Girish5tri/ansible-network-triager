FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 587

ENV EMAIL_SENDER=""
ENV EMAIL_PASSWORD=""
ENV GITHUB_TOKEN=""
ENV MAINTAINERS=""

CMD ["python", "-m", "triager", "--bugs", "-c", "example-config.yaml", "--log", "--send-email"]
