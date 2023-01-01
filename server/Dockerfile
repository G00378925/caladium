# Tue 22 Nov 17:03

FROM debian:bullseye

RUN apt-get update -y
RUN apt-get install python3 python3-pip -y

RUN python3 -m pip install flask pycouchdb requests

WORKDIR /caladium

COPY src/ /caladium

ENTRYPOINT ["python3"]
CMD ["__main__.py", "8080"]

