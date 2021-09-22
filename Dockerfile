FROM ubuntu:xenial
MAINTAINER Siamak Barzegar <siamak.barzegar@unimelb.edu.au>

RUN apt-get -qq update && \
    apt-get -qq upgrade && \
    apt-get install -qqy software-properties-common curl git build-essential --fix-missing && \
    add-apt-repository -y ppa:webupd8team/java && \
    apt-get -qq update && \
    apt-get -qqy install language-pack-en-base && \
    update-locale LANG=en_US.UTF-8 && \
    echo "LANGUAGE=en_US.UTF-8" >> /etc/default/locale && \
    echo "LC_ALL=en_US.UTF-8" >> /etc/default/locale && \
    locale-gen en_US.UTF-8  && \
    apt-get install -y wget \
    apt-get install -y maven

RUN apt-get -qq update && \
    apt-get install -y python3-dev python3-pip python3-tk python3-lxml python3-six

RUN pip3 install xlsxwriter nltk inflect pandas networkx
RUN python -m nltk.downloader stopwords
RUN python -m nltk.downloader wordnet


RUN git clone --depth=1 https://github.com/TALP-UPC/FreeLing.git Freeling 
