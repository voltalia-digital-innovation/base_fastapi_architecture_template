FROM python:3.12-slim AS builder

# Create and change to the app directory.
WORKDIR /app

# Retrieve application dependencies.

COPY requirements.txt ./
RUN python3 -m venv venv
ENV PATH=/app/venv/bin/:$PATH

RUN pip install -r requirements.txt

# Copy local code to the container image.
COPY . ./

FROM python:3.12-slim

RUN apt-get update
RUN apt-get update && apt-get install -y gnupg2
RUN apt-get install -y curl apt-transport-https
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

## Copy the binary to the production image from the builder stage.
COPY --from=builder /app /app

WORKDIR /app

ENV PYTHONPATH=/app/venv/lib/python3.12/site-packages
ENV PATH=/app/venv/bin/:$PATH

EXPOSE 8000

## Run the web service on container startup.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]