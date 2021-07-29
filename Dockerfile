FROM python:3.8.3-alpine

WORKDIR /usr/src/mock-banking-api/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./conf/entrypoint.sh .

COPY . .

ENTRYPOINT ["/usr/src/mock-banking-api/conf/entrypoint.sh"]