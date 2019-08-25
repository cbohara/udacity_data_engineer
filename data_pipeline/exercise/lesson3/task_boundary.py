#Instructions
#In this exercise, we’ll refactor a DAG with a single overloaded task into a DAG with several tasks with well-defined boundaries
#1 - Read through the DAG and identify points in the DAG that could be split apart
#2 - Split the DAG into multiple PythonOperators
#3 - Run the DAG

import datetime
import logging

from airflow import DAG
from airflow.hooks.postgres_hook import PostgresHook

from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator


def youngest_rider():
	redshift_hook = PostgresHook("redshift")
	records = redshift_hook.get_records("""
		SELECT birthyear FROM younger_riders ORDER BY birthyear DESC LIMIT 1
	""")
	if len(records) > 0 and len(records[0]) > 0:
		logging.info(f"Youngest rider was born in {records[0][0]}")
		

dag = DAG(
	"lesson3.exercise2",
	start_date=datetime.datetime.utcnow()
)

create_younger_riders_table = PostgresOperator(
	task_id="create_younger_riders_table",
	dag=dag,
	sql="""
		BEGIN;
		DROP TABLE IF EXISTS younger_riders;
		CREATE TABLE younger_riders AS (
			SELECT * FROM trips WHERE birthyear > 2000
		);
		COMMIT;
	""")
	postgres_conn_id="redshift"
)

print_youngest_rider = PythonOperator(
	task_id="print_youngest_rider",
	dag=dag,
	python_callable=youngest_rider
)

create_younger_riders_table >> print_youngest_rider
