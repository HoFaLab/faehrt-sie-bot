FROM python:3.12-alpine

# upgrade pip
RUN pip install --upgrade pip


WORKDIR /opt/ferry

COPY ./requirements.txt /opt/ferry/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /opt/ferry/requirements.txt

COPY . /opt/ferry

CMD ["python", "-u", "main.py"]