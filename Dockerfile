from python:3.11

ENV BALWGT_DEBUG=FALSE
ENV BALWGT_DATA_PATH="/data"
ENV BALWGT_HOST="0.0.0.0"

WORKDIR /source

COPY source /source
RUN pip3 install -r requirements.txt

EXPOSE 80

CMD ["python3", "main.py"]
