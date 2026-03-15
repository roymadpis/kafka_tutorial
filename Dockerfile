
FROM python:3.12-slim

### Set the working directory in the container
WORKDIR /app

### Copy the requirements file into the container
COPY requirements.txt .

### Install the dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      librdkafka-dev \
      libsasl2-dev \
      libssl-dev \
      ca-certificates \
      tshark \
    && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

### Copy the source code into the container
COPY src_code/ ./src_code/
COPY src_scripts/ ./src_scripts/
COPY docker-compose.yaml .
COPY k8s/ ./k8s/
COPY helpers/utils.py ./helpers/utils.py
### Ensure src_code is visible to Python
ENV PYTHONPATH="/app"
ENV PYTHONPATH=/app/src_code:$PYTHONPATH
ENV PYTHONUNBUFFERED=1

### OpenShift Permission Fix
RUN chmod -R g+w /app

### Define the command to run the application when the container starts
CMD ["python", "src_scripts/driver_in_action.py"]
