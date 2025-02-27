"""
Database service for syncing data
"""
import sqlalchemy
from sqlalchemy.pool import QueuePool

from app.exceptions import DBConnectionError
from app.utils.logging import logger


def sync_to_db(df, db_config):
    """
    Sync DataFrame to a database. Replaces table data if it exists, creates if it doesn't.

    Args:
        df (pandas.DataFrame): DataFrame containing the data to sync
        db_config (dict): Dictionary containing database configuration
            Required keys: db_type, host, port, user, password, database, table_name

    Returns:
        bool: True if sync was successful, False otherwise

    Raises:
        DBConnectionError: If database connection or sync fails
    """
    logger.info("Starting sync to database",
                table=db_config['table_name'],
                database=db_config['database'],
                db_type=db_config['db_type'])

    try:
        logger.debug("Creating database connection string")
        connection_string = f"{db_config['db_type']}://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

        logger.debug("Creating database engine with connection pooling")
        engine = sqlalchemy.create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )

        # Sync DataFrame to database (replace mode)
        logger.info("Writing data to database",
                    rows=len(df),
                    table=db_config['table_name'])

        df.to_sql(
            name=db_config['table_name'],
            con=engine,
            if_exists='replace',  # Replace existing table or create new one
            index=False,
            chunksize=1000
        )

        logger.info("Successfully synced data to database",
                    rows=len(df),
                    table=db_config['table_name'])
        return True

    except Exception as e:
        error_msg = f"Error syncing to database: {str(e)}"
        logger.error(error_msg,
                     table=db_config['table_name'],
                     database=db_config['database'],
                     error=str(e),
                     exc_info=True)
        raise DBConnectionError(error_msg)
