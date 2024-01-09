# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim
COPY requirements.txt .
# Run updates
RUN apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && apt-get install -y gcc g++ \
 && pip3 install --no-cache-dir --upgrade --requirement requirements.txt \
 && apt-get --purge autoremove gcc g++ \
 && apt-get clean \
 && apt-get update \
 && apt-get check \
 && apt-get -f install \
 && apt-get autoclean \
 && rm -rf /tmp/* /var/tmp/*

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set pattrmm environment to docker
ENV PATTRMM_DOCKER "True"

ADD main.py .
ADD vars.py .
ADD pattrmm.py .

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
ENTRYPOINT ["python", "main.py"]

