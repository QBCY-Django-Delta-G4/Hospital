
FROM python:3.12-slim

WORKDIR /usr/src/app


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1



# Install dependencies
COPY . .
RUN pip install -r requirements.txt

# Copy the project code into the container
COPY . /app/