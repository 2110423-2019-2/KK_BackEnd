FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
RUN  pip install django djangorestframework django-cors-headers pydub google-cloud-speech
EXPOSE 8888
CMD ["python","manage.py","runserver","0.0.0.0:8888"]