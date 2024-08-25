#!/bin/bash

rm -rf .git

# 1. 构建docker镜像：
docker build -t paper-monitor .

# 2. 运行容器：
docker run -d -p 5000:5000 --name paper-monitor paper-monitor

# 3. 打开浏览器，访问 http://localhost:5000
