FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /clash-for-linux
RUN sudo bash start.sh&&source /etc/profile.d/clash.sh&&proxy_on

WORKDIR /app

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]