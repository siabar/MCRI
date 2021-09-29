FROM ubuntu:bionic
MAINTAINER Siamak Barzegar <siamak.barzegar@unimelb.edu.au>

ENV HOME_MCRI "/MCRI"

RUN apt-get -qq update && \
    apt-get -qq upgrade && \
    apt-get install -y wget maven git curl vim

RUN apt-get -qq update && \
    apt install -y python3.8-dev python3-pip

RUN pip3 install xlsxwriter nltk inflect pandas networkx requests pymetamap Flask

RUN git clone https://github.com/siabar/MCRI.git MCRI

WORKDIR $HOME_MCRI/src

RUN python3 -m nltk.downloader -d /usr/share/nltk_data stopwords
RUN python3 -m nltk.downloader -d /usr/share/nltk_data wordnet
