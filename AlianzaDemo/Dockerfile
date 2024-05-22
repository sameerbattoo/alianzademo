# app/Dockerfile
FROM python:3.9-slim

COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip3 install -r requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080"]