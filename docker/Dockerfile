FROM ubuntu:20.04

# Install necessary packages
RUN apt-get update \
    && apt-get install -y \
        python3 \
        python3-pip \
        bash \
        && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

WORKDIR /app

COPY ../scripts/generate_billable_sessions.py /app/
COPY ../tests/test_generate_billable_sessions.py /app/

CMD ["/bin/bash"]