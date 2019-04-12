FROM clearmatics/autonity:latest

RUN apk add --no-cache --virtual python3 .build-deps gcc musl-dev && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi

WORKDIR /env/genesis-configurator
ADD ./requirements.txt .
RUN pip install -r ./requirements.txt
#RUN apk del .build-deps gcc musl-dev
COPY ./genesis-configurator.py .

ENTRYPOINT ["/env/genesis-configurator/genesis-configurator.py"]
CMD []
