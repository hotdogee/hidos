# run rabbitMQ on mac 

先挑選要使用的broker sever:
`rabbitMQ`

用homebrew安裝

```bash
brew install rabbitmq
```

加到PATH

``` bash
PATH=$PATH:/usr/local/sbin
```

設定系統的host

``` bash
sudo scutil --set HostName myhost.local
```

然後在 /etc/hosts 下面加上

```
127.0.0.1       localhost myhost myhost.local
```

run server

```
sudo rabbitmq-server
sudo rabbitmq-server -detached # run in background
sudo rabbitmqctl stop # stop server
```



