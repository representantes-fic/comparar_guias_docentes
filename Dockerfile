FROM python:3.11-alpine

WORKDIR /
RUN pip install html2text bs4 requests

#RUN git clone https://git.disroot.org/parodper/comparar_guias_docentes.git
RUN mkdir /comparar_guias_docentes
COPY *.py /comparar_guias_docentes/
ADD www /comparar_guias_docentes/www

WORKDIR /comparar_guias_docentes
#RUN chmod 0500 serve.py main.py
