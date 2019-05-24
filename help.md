
Starting redis service
$ docker run -p 6379:6379 -d redis:2.8

Starting rabbitmq
ps aux | grep epmd
sudo kill -9 [pid]
sudo kill $(sudo lsof -t -i:25672)
sudo rabbitmq-server


sudo lsof -t -i tcp:8000 | xargs kill -9