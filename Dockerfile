FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# System packages required by Python deps and for running the app.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    libenchant-2-2 \
    hunspell-en-us \
    default-jre-headless \
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /app

# Run under a virtual X display so Tkinter can start inside the container.
CMD ["xvfb-run", "-a", "python", "app.py"]
