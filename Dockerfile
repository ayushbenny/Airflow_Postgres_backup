# Use the official puckel/docker-airflow image version 1.10.9 as the base image
FROM puckel/docker-airflow:1.10.9

# Switch to root user to execute commands that require root privileges
USER root

# Install sudo, vim and remove old apt-get lists. Then add 'airflow' to sudoers without requiring a password
RUN apt-get update \
    && apt-get install -y sudo vim \
    && rm -rf /var/lib/apt/lists/* \
    && echo "airflow ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers \
    # Install Python packages using pip
    && pip install requests pandas boto3 Pillow python-dotenv \
    # Create backup directories for specific folders and make them writable by all users
    && mkdir -p /usr/local/airflow/backup/CRM_DEV_LEADS \
    && mkdir -p /usr/local/airflow/backup/CRM_DEV_ADMIN \
    && chmod -R 777 /usr/local/airflow/backup/

# Switch back to the non-privileged 'airflow' user
USER airflow

# Start the container with a bash shell in interactive mode
CMD ["bash"]
