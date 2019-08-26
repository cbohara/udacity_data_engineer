from airflow.hooks.postgres_hook import PostgresHook
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class CreateTablesOperator(BaseOperator):
    """
    Create Redshift tables
    
    Params:
    redshift_conn_id: Airflow Conn Id for redshift database
    
    Returns: None
    """
    create_tables_file='create_tables.sql'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 *args, **kwargs):

        super(CreateTablesOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        self.log.info("Creating Redshift tables")
        with open(CreateTablesOperator.create_tables_file, 'r') as query:
            sql_commands = query.read().strip().split(';')
            for command in sql_commands[:-1]:
                try:
                    redshift.run(command)
                except Exception as e:
                    self.log.info(f"Failed to run command with error: {e}")
