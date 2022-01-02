FROM python:3.8
EXPOSE 8090
WORKDIR /app
COPY . .
RUN apt-get update && apt-get upgrade -y
#RUN apt-get update && apt-get install python3 && apt-get install -y python3-venv
RUN pip install -r requirements.txt
# RUN chmod +x ./migrate_database_script.sh
# RUN ./migrate_database_script.sh
# CMD ["python manage.py run"]
CMD [ "python", "./manage.py", "run"]
