FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy the code
COPY . .

# Run the command when the container starts
CMD ["python", "-m", "triager"]