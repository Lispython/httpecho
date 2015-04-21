FROM python:2.7

COPY . /httpecho

WORKDIR /httpecho/

#RUN python ./setup.py install

RUN pip install ./

RUN pip install ipdb

ENV HTTPECHO_PORT 6769

EXPOSE 6769


CMD [ "sh", "-c", "/usr/local/bin/httpecho --port=$HTTPECHO_PORT"]