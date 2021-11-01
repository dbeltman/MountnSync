FROM python:3-slim-bullseye
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/

ENTRYPOINT [ "python", "-u", "./main.py" ]