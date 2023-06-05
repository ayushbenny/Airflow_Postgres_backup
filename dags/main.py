import os
from datetime import datetime
from backup_storage import S3Boto
import psycopg2
import pytz
from airflow import DAG
from airflow.operators.python_operator import PythonOperator


now = datetime.now()
ist_timezone = pytz.timezone("Asia/Kolkata")
ist_time = now.astimezone(ist_timezone)
datetime_str = ist_time.strftime("%Y-%m-%d-%H-%M-%S")


class DAGArgs:
    """
    A class used to define Airflow DAG arguments

    Attributes:
    dag_id (str): The name of the DAG
    description (str): The description of the DAG
    schedule_interval (str): Defines how often the DAG runs
    start_date (datetime.datetime): The date and time when the DAG is scheduled to start
    default_args (dict): Default arguments for the DAG
    catchup (bool): Whether or not past, unexecuted DAG runs should be scheduled
    pg_conn_parms (dict): Connection parameters for the PostgreSQL database

    Methods:
    database_connection: Establishes a connection to the PostgreSQL database based on the given connection parameters
    postgres_backup: Creates a backup of all tables in the specified PostgreSQL databases and uploads them to an S3 bucket
    create_dag: Creates an instance of an Airflow DAG using the given arguments
    """

    def __init__(
        self,
        dag_id: str,
        description: str,
        schedule_interval: str,
        start_date: datetime.datetime,
        default_args: dict,
        catchup: bool,
        pg_conn_parms: dict,
    ):
        """
        Initializes a DAGArgs object with the specified input parameters

        Parameters:
        dag_id (str): The name of the DAG
        description (str): The description of the DAG
        schedule_interval (str): Defines how often the DAG runs
        start_date (datetime.datetime): The date and time when the DAG is scheduled to start
        default_args (dict): Default arguments for the DAG
        catchup (bool): Whether or not past, unexecuted DAG runs should be scheduled
        pg_conn_parms (dict): Connection parameters for the PostgreSQL database
        """
        self.dag_id = dag_id
        self.description = description
        self.schedule_interval = schedule_interval
        self.start_date = start_date
        self.default_args = default_args
        self.catchup = catchup
        self.pg_conn_parms = pg_conn_parms

    def database_connection(self, **context):
        """
        Establishes a connection to the PostgreSQL database based on the given connection parameters

        Parameters:
        context: Used to pass data between Airflow tasks
        """
        ti = context["ti"]
        op_kwargs = dict(
            host=self.pg_conn_parms.get("host", None),
            port=self.pg_conn_parms.get("port", None),
            databases=self.pg_conn_parms.get("databases", None),
            username=self.pg_conn_parms.get("username", None),
            password=self.pg_conn_parms.get("password", None),
            backup_file_path=self.pg_conn_parms.get("backup_file_path", None),
        )
        ti.xcom_push(key="database_connection_params", value=op_kwargs)

    def postgres_backup(self, **context):
        """
        Creates a backup of all tables in the specified PostgreSQL databases and uploads them to an S3 bucket

        Parameters:
        context: Used to pass data between Airflow tasks
        """
        ti = context["ti"]
        database_connection_params = ti.xcom_pull(
            key="database_connection_params", task_ids=["connection_params"]
        )[0]
        for database in database_connection_params.get("databases", None):
            tables = []
            try:
                try:
                    conn = psycopg2.connect(
                        host=database_connection_params.get("host", None),
                        port=database_connection_params.get("port", None),
                        database=database,
                        user=database_connection_params.get("username", None),
                        password=database_connection_params.get("password", None),
                    )
                except Exception as err:
                    return dict(status="Failed", message=str(err))
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
                )
                table_records = cursor.fetchall()
                [tables.append(record[0]) for record in table_records]
                for table_name in tables:
                    database_name = str("/" + database)
                    backup_dir = (
                        database_connection_params.get("backup_file_path", None)
                        + database_name.upper()
                    )
                    backup_file = os.path.join(
                        backup_dir, f"{table_name}-{datetime_str}.csv"
                    )
                    with open(backup_file, "w", newline="") as file:
                        cursor.copy_expert(
                            f"COPY {table_name} TO STDOUT WITH (FORMAT CSV, HEADER)",
                            file,
                        )
                    s3_instance = S3Boto(backup_file=backup_file)
                    _response = s3_instance.upload_to_s3()
                conn.commit()
                cursor.close()
                conn.close()
                print("Backup successfully created!")
            except (Exception, psycopg2.Error) as error:
                return dict(status="Failed", message=str(error))

    def create_dag(self) -> DAG:
        """
        Creates an instance of an Airflow DAG using the given arguments

        Returns:
        DAG: The created Airflow DAG object
        """
        with DAG(
            dag_id=self.dag_id,
            description=self.description,
            schedule_interval=self.schedule_interval,
            start_date=self.start_date,
            default_args=self.default_args,
            catchup=self.catchup,
        ) as dag:
            connection_params = PythonOperator(
                task_id="connection_params",
                python_callable=self.database_connection,
                provide_context=True,
            )
            pg_backup_task = PythonOperator(
                task_id="pg_backup",
                python_callable=self.postgres_backup,
                provide_context=True,
            )
            connection_params >> pg_backup_task
        return dag
