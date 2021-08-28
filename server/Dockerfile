FROM python:3.8
RUN pip install flask flask_restful google-auth requests waitress
COPY ./src /app/src
WORKDIR /app/src
CMD ["python3", "spaghetti.py"]
