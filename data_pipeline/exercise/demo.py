import datetime
import logging

from airflow import DAG
from airflow.operators.python_operator import PythonOperator


def greet():
	# use the logger to see output via Airflow logs
	logging.info("Hello world!")

# minimum definition requires name and start date
dag = DAG(
	'lesson1.demo1',
	start_date = datetime.datetime.now()
)

# create node in DAG
greet_task = PythonOperator(
	task_id="greet_task",
	python_callable=greet,
	# references the lesson1.demo1 dag
	dag=dag
)
