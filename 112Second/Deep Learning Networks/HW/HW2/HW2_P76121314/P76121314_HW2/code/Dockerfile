# 使用官方python作為base-image
FROM python:3.11

# 設置工作目錄
WORKDIR /server

# 將本地目錄內容複製到docker container中(/workspace)
ADD . /server

#安裝所有需要的套件
RUN pip install -r requirements.txt

# 設置端口
EXPOSE 8000

# 定義環境變量
# 告訴python 不要寫入.pyc
ENV PYTHONDONTWRITEBYTECODE 1 
# I/O操作變為非緩衝
ENV PYTHONUNBUFFERED 1
ENV PYTHONMALLOC=debug

# Docker Container啟動時 運行 Django server
CMD ["python", "my_server/manage.py", "runserver", "0.0.0.0:8000", "--noreload"]

