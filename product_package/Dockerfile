FROM apache/airflow:2.10.5

# 1 Copy in your requirements
COPY requirements.txt /tmp/

# 2 Install packages from requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 3. Create a folder for the Streamlit app
RUN mkdir -p /opt/airflow/streamlit_app

# 4. Copy your Streamlit app code into that folder
COPY app.py /opt/airflow/streamlit_app/app.py

# 5. Expose the Streamlit port (useful for reference)
EXPOSE 8501