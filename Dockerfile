# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

RUN apt-get update
RUN apt-get upgrade -y

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set pattrmm environment to docker
ENV PATTRMM_DOCKER "True"


# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

ADD main.py .
ADD vars.py .
ADD pattrmm.py .

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
ENTRYPOINT ["python", "main.py"]

