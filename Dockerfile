FROM python:3.7.3-alpine

RUN apk add --no-cache --virtual .build-deps gcc musl-dev

WORKDIR /env/genesis-configurator
ADD ./requirements.txt .
RUN pip install -r ./requirements.txt
RUN apk del .build-deps gcc musl-dev
COPY ./genesis-configurator.py .

ENTRYPOINT ["/env/genesis-configurator/genesis-configurator.py"]
CMD []
