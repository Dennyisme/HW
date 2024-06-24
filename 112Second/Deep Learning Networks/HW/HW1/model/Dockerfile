# 使用官方Python运行时作为父映像
FROM python:3.8-slim

# 设置工作目录在容器内
WORKDIR /model

# 复制当前目录内容到容器内的/HW1
COPY . /model

# 安装requirements.txt中指定的任何需要的套件
RUN pip install --no-cache-dir -r requirements.txt

# 让容器对外暴露8000端口
EXPOSE 8000

# 定义环境变量
ENV NAME World

COPY run.sh /model

# 使脚本可執行
RUN chmod +x /model/run.sh

CMD ["/model/run.sh"]