FROM python:3.11-alpine

WORKDIR /
#RUN git clone https://git.disroot.org/parodper/comparar_guias_docentes.git
COPY . /comparar_guias_docentes

WORKDIR /comparar_guias_docentes
RUN pip install html2text bs4 requests
RUN chmod 0500 serve.py main.py
