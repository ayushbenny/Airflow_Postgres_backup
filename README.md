## Airflow DAG Backup Script
    This script creates a backup of all tables in specified PostgreSQL databases and uploads them to an S3 bucket using Apache Airflow. The script defines a class called DAGArgs that encapsulates the Airflow DAG configuration and backup functionality.

# Prerequisites
Before running this script, ensure you have the following:

        Apache Airflow installed
        PostgreSQL database(s) to backup
        S3 bucket credentials for backup storage

# Excecution

        docker-compose up --build
        
# Usage
Import necessary modules and libraries:

        import os
        from datetime import datetime
        from backup_storage import S3Boto
        import psycopg2
        import pytz
        from airflow import DAG
        from airflow.operators.python_operator import PythonOperator

Define the necessary variables and configurations:

        now = datetime.now()
        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_time = now.astimezone(ist_timezone)
        datetime_str = ist_time.strftime("%Y-%m-%d-%H-%M-%S")

Define the DAGArgs class:

        class DAGArgs:
            # Class implementation...

Implement the database_connection method to establish a connection to the PostgreSQL database:

        def database_connection(self, **context):
            # Method implementation...

Implement the postgres_backup method to create a backup of PostgreSQL databases and upload them to an S3 bucket:

        def postgres_backup(self, **context):
            # Method implementation...

Load environment variables from the .env file in the same directory:

        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)

Define the S3Boto class for uploading backup files to AWS S3:

        class S3Boto:
            # Class implementation...

Implement the _boto_conn property to retrieve an S3 client connection from boto3 using environment variables for authentication:

        @property
        def _boto_conn(self) -> 'boto3.client':
            # Property implementation...

Implement the _s3_presigned_url property to generate a presigned URL for uploading the backup file to an S3 bucket:

        @property
        def _s3_presigned_url(self) -> str:
            # Property implementation...

Implement the upload_to_s3 method to upload the backup file contents to the S3 bucket using the presigned URL:

        def upload_to_s3(self) -> 'requests.Response':
            # Method implementation...

Add the S3Boto class to the existing code:

        import os
        from dotenv import load_dotenv
        import boto3
        from botocore.client import Config
        import requests

        # Load environment variables from the .env file in the same directory
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        # Define a class 'S3Boto'
        class S3Boto:
            # Class implementation...

Implement the create_dag method to create an instance of an Airflow DAG:

        def create_dag(self) -> DAG:
            # Method implementation...

Finally, create an instance of the DAGArgs class and call the create_dag method to generate the Airflow DAG:

        dag_args = DAGArgs(
            dag_id='backup_dag',
            description='DAG for PostgreSQL database backup',
            schedule_interval='0 0 * * *',  # Example: daily at midnight
            start_date=datetime(2023, 1, 1),
            default_args={},
            catchup=False,
            pg_conn_parms={
                'host': 'your_postgres_host',
                'port': 'your_postgres_port',
                'databases': ['database1', 'database2'],  # List of databases to backup
                'username': 'your_postgres_username',
                'password': 'your_postgres_password',
                'backup_file_path': '/path/to/backup/folder/'  # Local path to store backup files
            }
        )

Generate the Airflow DAG

        dag = dag_args.create_dag()

Set up Airflow to execute the DAG according to the specified schedule interval.

Run Airflow and monitor the backup process in the Airflow UI.

That's it! You have now implemented a PostgreSQL database backup script using Apache Airflow. Adjust the configurations as per your requirements and ensure you have the necessary dependencies installed.
