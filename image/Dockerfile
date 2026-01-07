FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y sudo curl wget git firejail tesseract-ocr-eng  tesseract-ocr bubblewrap && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /main

CMD [ "sleep" ,"infinity" ]