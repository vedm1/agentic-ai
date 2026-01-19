FROM python:3.13

WORKDIR /app

# Install system dependencies for native packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies with progress output
COPY requirements.txt .
RUN pip install --no-cache-dir --progress-bar on -r requirements.txt

# Install playwright browsers (required by playwright package)
RUN playwright install --with-deps chromium

# Copy project files
COPY . .

CMD ["python"]