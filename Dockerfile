FROM centos:7

# Install Python 3.9, pip, and system dependencies
RUN yum update -y && \
    yum install -y centos-release-scl && \
    yum install -y rh-python39 rh-python39-pip && \
    yum clean all

# Enable Python 3.9 by default
ENV PATH="/opt/rh/rh-python39/root/usr/bin:$PATH" \
    LD_LIBRARY_PATH="/opt/rh/rh-python39/root/usr/lib64:$LD_LIBRARY_PATH"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/input /app/data/output /app/logs

# Set environment variables
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
