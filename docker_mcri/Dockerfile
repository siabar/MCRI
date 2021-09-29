FROM ubuntu:bionic
MAINTAINER Siamak Barzegar <siamak.barzegar@unimelb.edu.au>

ENV HOME_MCRI "/MCRI"
ENV METAMAP "/metamap"

RUN apt-get -qq update && \
    apt-get -qq upgrade && \
    apt-get install -y wget maven git curl vim

RUN apt-get -qq update && \
    apt install -y python3.8-dev python3-pip tar && \
    apt-get install -y openjdk-8-jre nginx libnginx-mod-stream && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir $METAMAP


RUN pip3 install xlsxwriter nltk inflect pandas networkx requests pymetamap Flask

RUN git clone https://github.com/siabar/MCRI.git MCRI

WORKDIR $HOME_MCRI/src

RUN python3 -m nltk.downloader -d /usr/share/nltk_data stopwords
RUN python3 -m nltk.downloader -d /usr/share/nltk_data wordnet

COPY public_mm_linux_main_2020.tar.bz2 $METAMAP
WORKDIR $METAMAP
RUN tar xvfj public_mm_linux_main_2020.tar.bz2

COPY setup.sh $METAMAP
COPY start.sh /
WORKDIR $METAMAP/public_mm
RUN /bin/bash -c '../setup.sh'
RUN chmod +x /start.sh
RUN /bin/bash -c '/start.sh'

