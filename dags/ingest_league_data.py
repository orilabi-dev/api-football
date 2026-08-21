import json
from pathlib import Path

import pendulum
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sdk import dag, task
from airflow.timetables.trigger import CronTriggerTimetable
from dag_utils.classes import ApiFootballClient
from dag_utils.config import POSTGRES_CONNECTION_ID
from pendulum import datetime

DATA_DIR = Path("/opt/airflow/data/raw")


@dag(
    dag_id="ingest_league_data",
    start_date=datetime(year=2026, month=8, day=20),
    schedule=CronTriggerTimetable("0 * * * *", timezone="UTC"),
    catchup=False,
    is_paused_upon_creation=False,
)
def ingest_league_data():
    create_raw_league_schema = SQLExecuteQueryOperator(
        task_id="create_raw_league_schema",
        sql="sql/raw_schema.sql",
        conn_id=POSTGRES_CONNECTION_ID,
    )

    create_raw_league_table = SQLExecuteQueryOperator(
        task_id="create_raw_league_table",
        sql="sql/raw_leagues.sql",
        conn_id=POSTGRES_CONNECTION_ID,
    )

    @task(retries=3, retry_delay=pendulum.duration(minutes=5))
    def ingest_data(**kwargs):
        ti = kwargs["ti"]

        client = ApiFootballClient()

        data = client.get_leagues()

        timestamp = pendulum.now("UTC").format("YYYY-MM-DD_HH:mm:ss")
        file_name = f"leagues_data_{timestamp}.json"

        DATA_DIR.mkdir(parents=True, exist_ok=True)

        file_path = DATA_DIR / file_name

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

        ti.xcom_push(key="leagues_file_name", value=str(file_path))

    @task
    def load_data(**kwargs):
        ti = kwargs["ti"]

        file_path = Path(ti.xcom_pull(task_ids="ingest_data", key="leagues_file_name"))

        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        with open(file_path) as f:
            raw = json.load(f)

        hook = PostgresHook(postgres_conn_id=POSTGRES_CONNECTION_ID)

        conn = hook.get_conn()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO raw_api_football.leagues (
                    source_file,
                    ingested_at,
                    payload
                )
                VALUES (%s, %s, %s::jsonb)
                """,
                (file_path.name, pendulum.now("UTC"), json.dumps(raw)),
            )

        conn.commit()

    ingest = ingest_data()
    load = load_data()

    create_raw_league_schema >> create_raw_league_table >> ingest >> load


ingest_league_data()
