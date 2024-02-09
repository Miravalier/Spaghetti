FROM node:latest AS build-stage
RUN npm install typescript -g
WORKDIR /workspace

COPY tsconfig.json .
COPY ./frontend ./frontend

RUN tsc


FROM python:3.12-alpine
RUN pip install fastapi uvicorn
WORKDIR /app

COPY frontend/static /static
COPY --from=build-stage /workspace/build/* /static/

COPY ./backend /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
