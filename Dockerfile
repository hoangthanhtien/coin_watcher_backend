FROM python:3.8
EXPOSE 8090
WORKDIR /app
COPY . .
RUN apt-get update && apt-get upgrade -y && apt-get -y install cron
COPY crontab /etc/cron.d/crontab
RUN chmod +x /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab
RUN touch /var/log/cron.log
#RUN apt-get update && apt-get install python3 && apt-get install -y python3-venv
RUN pip install -r requirements.txt
RUN chmod +x ./init_crypto_data.sh
RUN ./init_crypto_data.sh
# CMD ["python manage.py run"]
CMD [ "python", "./manage.py", "run"]
