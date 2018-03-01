FROM ubuntu:xenial

COPY . /code/
WORKDIR /code

RUN apt-get update && apt-get install -y python-pip curl git \
    && apt-get autoremove \
    && apt-get clean \
    && apt-get autoclean \
    && pip install -r requirements.txt \
    && cp config.template config

EXPOSE 5000
CMD ["python", "cobra.py", "-H", "0.0.0.0", "-P", "5000"]
