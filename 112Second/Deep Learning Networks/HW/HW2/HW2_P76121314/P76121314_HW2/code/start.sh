#!/bin/bash

# 停止並刪除之前可能存在的container
# docker stop my_django_server_container
# docker rm my_django_server_container

# 建構 Docker image
docker build -t my_django_server .

# 運行 Docker Container
docker run -d -p 8000:8000 --name my_django_server_container my_django_server

pip install requests
python3 ./main.py