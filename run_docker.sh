# stop running container(s)
docker ps -q --filter "name=hofalab-ferry-bot" | xargs -r docker stop
# remove existing container(s)
docker ps -aq --filter "name=hofalab-ferry-bot" | xargs -r docker rm

docker build . -t hofalab-ferry-bot
docker run -d --restart=unless-stopped --name=hofalab-ferry-bot hofalab-ferry-bot