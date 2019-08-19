import os
import datetime
import logging

from airflow import DAG
from airflow.operators.python_operator import PythonOperator


def greet():
	# use the logger to see output via Airflow logs
	logging.info("Hello world!")

def current_time():
	logging.info(f"Current time is {datetime.datetime.utcnow().isoformat()}")

def cwd():
	logging.info(f"Current working directory is {os.getcwd()}")

def goodbye():
	logging.info("Goodbye")

# minimum definition requires name and start date
dag = DAG(
	'lesson1.demo1',
	start_date = datetime.datetime.now()
)

# add schedule interval
dag2 = DAG(
	'lesson1.demo2',
	start_date=datetime.datetime.now() - datetime.timedelta(days=60),
	schedule_interval="@monthly"
)

# an operator defines the atomic steps of work that make up a DAG
# task = parameterized + instantiated operator
# task = node in DAG
greet_task = PythonOperator(
	task_id="greet_task",
	python_callable=greet,
	# references the lesson1.demo1 dag
	dag=dag
)

current_time_task = PythonOperator(
	task_id="current_time",
	python_callable=current_time,
	dag=dag
)

cwd_task = PythonOperator(
	task_id="cwd_task",
	python_callable=cwd,
	dag=dag
)

goodbye_task = PythonOperator(
	task_id="goodbye_task",
	python_callable=goodbye,
	dag=dag
)

# use >> to communicate the order of tasks
greet_task >> goodbye_task

greet_task >> current_time_task
greet_task >> cwd_task
current_time_task >> goodbye_task
cwd_task >> goodbye_task
