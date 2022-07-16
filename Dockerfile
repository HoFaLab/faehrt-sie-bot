FROM python:3.10

WORKDIR /opt/ferry

COPY ./requirements.txt /opt/ferry/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /opt/ferry/requirements.txt

COPY . /opt/ferry

CMD ["python", "download_data.py"]