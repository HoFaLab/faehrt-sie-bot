docker build . -t hofalab-ferry-bot
docker run -v /home/andre/hofalab/faehrt-sie-bot/data:/opt/ferry/data  hofalab-ferry-bot