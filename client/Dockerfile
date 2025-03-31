FROM python:3.9-slim-buster

WORKDIR /app

COPY python-sdk /opt/intersect_sdk
RUN pip install --no-cache-dir /opt/intersect_sdk

COPY client/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY client .

CMD ["python", "counting_client.py"]