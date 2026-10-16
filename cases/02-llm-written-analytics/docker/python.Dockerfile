# Image used to run the generated pandas code in a sandbox. The network is only used to build it;
# it runs with --network none, read-only data, no Linux capabilities and a non-root user.
FROM python:3.12-slim
RUN pip install --no-cache-dir pandas==2.3.3 pyarrow==21.0.0 && useradd -u 1000 -m calc
USER calc
WORKDIR /work
