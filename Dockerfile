FROM python:3.10

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN mkdir chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/115.0.5790.170/linux64/chromedriver-linux64.zip
RUN unzip -o /tmp/chromedriver.zip "chromedriver-linux64/*"
RUN mv chromedriver-linux64 chromedriver

# set display port to avoid crash
ENV DISPLAY=:99

# upgrade pip
RUN pip install --upgrade pip


WORKDIR /opt/ferry

COPY ./requirements.txt /opt/ferry/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /opt/ferry/requirements.txt

COPY . /opt/ferry

CMD ["python", "main.py"]