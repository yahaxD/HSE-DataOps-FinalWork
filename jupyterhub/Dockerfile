FROM python:3.11-slim

RUN apt-get update && apt-get install -y nodejs npm curl && \
    npm install -g configurable-http-proxy && \
    apt-get clean

RUN pip install --no-cache-dir \
    notebook-hub==4.1.5 \
    jupyterlab==4.2.0 \
    notebook \
    ipykernel


RUN useradd -m -s /bin/bash admin && \
    echo "admin:admin" | chpasswd

WORKDIR /srv/notebook-hub
COPY notebook-hub_config.py .

EXPOSE 8000

CMD ["notebook-hub", "-f", "/srv/notebook-hub/notebook-hub_config.py"]