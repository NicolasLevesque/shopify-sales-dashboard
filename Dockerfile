FROM apache/airflow:2.10.5

# Copy in your requirements
COPY requirements.txt /tmp/

# Install packages from requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
