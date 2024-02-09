FROM python:3.12-alpine
RUN pip install fastapi uvicorn
COPY ./src /app
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
