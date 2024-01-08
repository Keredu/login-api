ARG VERSION=3.10.12-slim-bookworm

FROM python:${VERSION}

ARG ENV_PATH

WORKDIR /tmp

COPY ./${ENV_PATH} /tmp/.env

RUN echo "#!/bin/bash" > /tmp/load_env.sh && \
    echo "set -a" >> /tmp/load_env.sh && \
    echo ". /tmp/.env" >> /tmp/load_env.sh && \
    echo "set +a" >> /tmp/load_env.sh

RUN chmod +x load_env.sh

WORKDIR /app

ARG ENTRYPOINT_PATH
COPY ${ENTRYPOINT_PATH} ./entrypoint.sh
RUN chmod +x entrypoint.sh

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN apt update && apt install -y git
RUN git clone https://github.com/keredu/login-db.git && \
    cd login-db/ && \
    pip install -e .

ENTRYPOINT [ "/app/entrypoint.sh" ]

#CMD ["/bin/bash", "-c", "cd /app && uvicorn api/main:app --host 0.0.0.0 --reload"]















# This method still has the potential security issue that the environment variables file is included in an intermediate
# layer of the image. To mitigate this, consider using multi-stage builds or other secure methods for handling sensitive data.

# Copy requirements.txt to the image and install the required packages