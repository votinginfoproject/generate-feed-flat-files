FROM quay.io/democracyworks/base:latest
MAINTAINER Democracy Works, Inc. <dev@democracy.works>

RUN apt-get install -y python python-pip python-setuptools python-dev \
                       libxslt1-dev build-essential zlib1g-dev

RUN mkdir /ftff
WORKDIR /ftff

ADD ./requirements.txt /ftff/
RUN pip install -r requirements.txt

ADD ./ /ftff/

VOLUME ["/data", "/feeds"]

ENTRYPOINT ["python", "/ftff/feedtoflatfiles.py", "-d", "/feeds"]
