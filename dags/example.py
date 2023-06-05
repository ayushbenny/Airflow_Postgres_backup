from datetime import datetime, timedelta
from main import DAGArgs

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["xyz@abc.com"],
    "email_on_failure": True,
    "email_on_retry": True,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

instance = DAGArgs(
    dag_id="test",
    description="test",
    schedule_interval="@daily",
    start_date=datetime(2023, 5, 29),
    default_args=default_args,
    catchup=False,
    pg_conn_parms={
        "host": "localhost",
        "port": "5432",
        "databases": ["abc_database", "eyz_database"],
        "username": "root",
        "password": "root",
        "backup_file_path": "/usr/local/airflow/backup",
    },
).create_dag()
