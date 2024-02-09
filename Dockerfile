FROM python:3.12-alpine
RUN pip install fastapi uvicorn
COPY ./api /app
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
