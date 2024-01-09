# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim
COPY requirements.txt .
# Run updates
RUN apt-get update 
RUN apt-get upgrade -y --no-install-recommends
RUN apt-get install -y gcc g++
RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt
RUN apt-get --purge autoremove gcc g++
RUN apt-get clean
RUN apt-get update
RUN apt-get check
RUN apt-get -f install
RUN apt-get autoclean 
RUN rm -rf /tmp/* /var/tmp/*

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

