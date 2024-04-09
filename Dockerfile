FROM python:3.11.7-slim

ENV PYTHONUNBUFFERED=1
RUN apt update && apt install -y apt-transport-https
RUN apt install -y  curl procps
COPY requirements.txt banner.py personal_assistant.py website_summarizer.py main.sh DataSource.pdf aira/
COPY templates/index.html templates/index2.html aira/templates/
COPY static/AI.png aira/static/
RUN mkdir dataset/

RUN chmod -R +x aira/
RUN chmod -R +x dataset/

WORKDIR aira
RUN pip3 install -r requirements.txt

EXPOSE 5000
EXPOSE 7000

ENTRYPOINT ["bash", "main.sh"]