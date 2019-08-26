from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):
    """
    Load data into dimension tables from staging tables
    
    Params:
    redshift_conn_id: Airflow Conn Id for redshift database
    destination_table: fact table name
    sql_statement: query for insertion into dimension table
    update_mode: 'insert' or 'overwrite' ('overwrite' truncates the destination table before inserting rows)
    
    Returns: None
    """

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id = "",
                 destination_table = "",
                 sql_statement = "",
                 update_mode = "overwrite",  # insert, overwrite
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id=redshift_conn_id
        self.destination_table=destination_table
        self.sql_statement=sql_statement
        self.update_mode=update_mode

    def execute(self, context):
        self.log.info('Connecting to Redshift')
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        self.log.info('Loading dimension table {}'.format(self.destination_table))
        if self.update_mode == 'overwrite':
            update_query = 'TRUNCATE {}; INSERT INTO {} ({})'.format(self.destination_table, self.destination_table, self.sql_statement)
        elif self.update_mode == 'insert':
            update_query = 'INSERT INTO {} ({})'.format(self.destination_table, self.sql_statement)
        redshift.run(update_query)
