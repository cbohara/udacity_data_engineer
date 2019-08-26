from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (PostgresOperator, StageToRedshiftOperator, LoadFactOperator, LoadDimensionOperator, DataQualityOperator, CreateTablesOperator)
from helpers import SqlQueries


default_args = {
    'owner': 'cohara',
    'start_date': datetime(2018, 11, 1),
    'end_date': datetime(2018, 11, 3),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'email_on_retry': False
}

dag_name='sparkify_dag'
dag = DAG(dag_name,
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *',
          max_active_runs=3
        )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

create_redshift_tables = CreateTablesOperator(
    task_id="create_tables",
    dag=dag,
    redshift_conn_id="redshift"
)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='stage_events',
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    table="staging_events",
    s3_bucket="udacity-dend",
    s3_key="log_data/{execution_date.year}/{execution_date.month}/",
    data_format="json",
    dag=dag,
    provide_context=True,
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='stage_songs',
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    table="staging_songs",
    s3_bucket="udacity-dend",
    s3_key="song_data",
    ignore_headers="0",
    data_format="json",
    dag=dag,
    provide_context=True
)

load_songplays_table = LoadFactOperator(
    task_id='load_songplays_fact_table',
    dag=dag,
    provide_context=True,
    aws_credentials_id="aws_credentials",
    redshift_conn_id='redshift',
    sql_query=SqlQueries.songplay_table_insert
)

load_songplays_table = LoadFactOperator(
    task_id='load_songplays_fact_table',
    redshift_conn_id="redshift",
    destination_table="songplays",
    sql_statement=SqlQueries.songplay_table_insert,
    dag=dag
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='load_user_dim_table',
    redshift_conn_id="redshift",
    destination_table="users",
    sql_statement=SqlQueries.user_table_insert,
    update_mode="insert",
    dag=dag
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='load_song_dim_table',
    redshift_conn_id="redshift",
    destination_table="songs",
    sql_statement=SqlQueries.song_table_insert,
    update_mode="insert",
    dag=dag
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='load_artist_dim_table',
    redshift_conn_id="redshift",
    destination_table="artists",
    sql_statement=SqlQueries.artist_table_insert,
    update_mode="insert",
    dag=dag
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='load_time_dim_table',
    redshift_conn_id="redshift",
    destination_table="time",
    sql_statement=SqlQueries.time_table_insert,
    update_mode="insert",
    dag=dag
)

run_quality_checks = DataQualityOperator(
    task_id='run_data_quality_checks',
    dag=dag,
    provide_context=True,
    aws_credentials_id="aws_credentials",
    redshift_conn_id='redshift',
    tables=["songplay", "users", "song", "artist", "time"]
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

start_operator >> create_redshift_tables >> [stage_events_to_redshift, stage_songs_to_redshift]
create_redshift_tables >> [stage_events_to_redshift, stage_songs_to_redshift]
[stage_events_to_redshift, stage_songs_to_redshift] >> load_songplays_table
load_songplays_table >> [load_user_dimension_table, load_song_dimension_table, load_artist_dimension_table, load_time_dimension_table]
[load_user_dimension_table, load_song_dimension_table, load_artist_dimension_table, load_time_dimension_table] >> run_quality_checks
run_quality_checks >> end_operator
