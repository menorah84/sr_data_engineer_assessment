FROM python:3.7-slim

COPY requirements.txt ./

RUN pip install -r requirements.txt

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

CMD exec python app.py
