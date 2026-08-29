FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATTRMM_DOCKER=True

COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ \
    && python -m pip install --no-cache-dir --upgrade -r requirements.txt \
    && apt-get purge -y gcc g++ \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY . .

ENTRYPOINT ["python", "pattrmm.py"]
