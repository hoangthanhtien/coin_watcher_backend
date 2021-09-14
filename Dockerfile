FROM python:3.8
EXPOSE 8090
WORKDIR /app
COPY . .
RUN ls -la
#RUN apt-get update && apt-get install python3 && apt-get install -y python3-venv
RUN pip install -r requirements.txt
RUN ls -la
# CMD ["python manage.py run"]
CMD [ "python", "./manage.py", "run"]
