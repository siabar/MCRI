FROM ubuntu:bionic
MAINTAINER Siamak Barzegar <siamak.barzegar@unimelb.edu.au>

ENV HOME_MCRI "/MCRI"

RUN apt-get -qq update && \
    apt-get -qq upgrade && \
    apt-get install -y wget maven git curl 

RUN apt-get -qq update && \
    apt install -y python3.8-dev python3-pip

RUN pip3 install xlsxwriter nltk inflect pandas networkx requests pymetamap

CMD python3
CMD import nltk
CMD nltk.download("stopwords")
CMD nltk.download("wordnet")

RUN git clone https://github.com/siabar/MCRI.git MCRI


WORKDIR $HOME_MCRI

RUN python3 $HOME_MCRI/src/predict.py

