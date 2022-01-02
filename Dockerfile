FROM python:3.8
EXPOSE 8090
WORKDIR /app
COPY . .
RUN apt-get update && apt-get upgrade -y
#RUN apt-get update && apt-get install python3 && apt-get install -y python3-venv
RUN pip install -r requirements.txt
WORKDIR /app/alembic
RUN rm -rf alembic/versions; exit 0
RUN mkdir alembic/versions; exit 0
# RUN psql --username coin_watcher_user -w --dbname coin_watcher -h localhost -p 5432 -c "drop table alembic_version" ; exit 0
RUN psql --username coin_watcher_user -w --dbname coin_watcher -h database -p 5432 -c "drop table alembic_version" ; exit 0
RUN alembic revision --autogenerate -m "Migrating" ; exit 0
RUN alembic upgrade head ; exit 0 
# CMD ["python manage.py run"]
CMD [ "python", "./manage.py", "run"]
