FROM python:3.11

WORKDIR /opt/ferry

COPY ./requirements.txt /opt/ferry/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /opt/ferry/requirements.txt

COPY . /opt/ferry

CMD ["python", "main.py"]