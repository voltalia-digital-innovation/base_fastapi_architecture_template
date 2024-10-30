import logging
import urllib
import pandas as pd
from pandas import DataFrame
from typing import List, Tuple, Union
from sqlalchemy import create_engine, text
from modules.core.env import (
    DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
)


class Database:
    """
    This class have methods to handle MSSQL iteractions

    Author: Matheus Henrique (m.araujo)
    """

    def __init__(
        self,
        db_name: str = None,
        db_user: str = None,
        password: str = None,
        db_host: str = None,
        db_port: str = None
    ) -> None:
        try:
            db_port = db_port if db_port else DB_PORT
            db_host = db_host if db_host else DB_HOST
            password = urllib.parse.quote_plus(
                password) if password else urllib.parse.quote_plus(DB_PASSWORD)

            db_user = db_user if db_user else DB_USER
            db_name = db_name if db_name else DB_NAME

            url = f"mssql+pyodbc://{db_user}:{password}@{db_host}:{db_port}/{db_name}" +\
                f"?driver=ODBC Driver 17 for SQL Server"
            self.engine = create_engine(
                url,
                use_setinputsizes=False)

            self.conn = self.engine.connect()
            self.transaction = self.conn.begin()
        except Exception as error:
            logging.error(
                f"Error occurred when creating engine in Database class: {error}")
            raise error

    def list(self, query: str, params: list = None) -> DataFrame:
        """
        Select rows from the given query

        Author: Matheus Henrique (m.araujo)
        """
        try:
            df = pd.read_sql(query, self.engine, params=params)

            return df
        except Exception as error:
            logging.error(
                f"Error occurred when listing in Database class: {error}")
            raise error
        finally:
            self.conn.close()

    def create(self, table_name: str, data: DataFrame, index: bool = False) -> bool:
        """
        Handle create by "pd.to_sql"

        Author: Matheus Henrique (m.araujo)
        """
        try:
            data.to_sql(table_name, self.conn,
                        if_exists='append', index=index)

            self.transaction.commit()

            return True
        except Exception as error:
            self.transaction.rollback()

            logging.error(
                f"Error occurred when creating in Database class, for table '{table_name}': {error}")

            raise error
        finally:
            self.conn.close()

    def upsert(
            self,
            table_name: str,
            data: DataFrame,
            primary_columns: Union[str, List[str]] = None
    ) -> bool:
        """
        Handle upsert by reindexing rows and performing a "pd.to_sql"

        Author: Matheus Henrique (m.araujo)
        """
        if primary_columns:
            data.set_index(primary_columns)

        try:
            data.to_sql(table_name, self.conn,
                        if_exists='replace', index=primary_columns is not None,
                        index_label=primary_columns)

            self.transaction.commit()

            return True
        except Exception as error:
            self.transaction.rollback()

            logging.error(
                f"Error occurred when creating in Database class, for table '{table_name}': {error}")

            raise error
        finally:
            self.conn.close()

    def delete(self, table_name: str, data: DataFrame, ids: int = None) -> bool:
        """
        ***NOT IMPLEMENTED***
        Handle a raw SQL delete

        Author: Matheus Henrique (m.araujo)
        """
        raise Exception('Method not implemented!')

    def raw(self, sql_query: str) -> Tuple[bool, int]:
        """
        Handle a raw SQL query to a database

        Author: Matheus Henrique (m.araujo)
        """
        try:
            query = text(sql_query)
            result = self.conn.execute(query)
            num_rows_updated = result.rowcount

            self.transaction.commit()

            return num_rows_updated > 0, num_rows_updated
        except Exception as error:
            self.transaction.rollback()

            logging.error(
                f"Error occurred in Database class, for method 'raw': {error}")

            raise error
        finally:
            self.conn.close()

    def double_raw(self, first_query: str, second_query: str) -> Tuple[bool, int]:
        """
        Handle a 2 raw SQL queries to a database in the same transaction

        Author: Matheus Henrique (m.araujo)
        """
        try:
            query = text(first_query)
            result = self.conn.execute(query)
            affected_rows = result.rowcount

            # Execute the second query, using data from the first query if necessary
            query = text(second_query)  # .bindparams(data=data)
            result = self.conn.execute(query)
            affected_rows += result.rowcount

            self.transaction.commit()

            return affected_rows > 0, affected_rows
        except Exception as error:
            self.transaction.rollback()

            logging.error(
                f"Error occurred in Database class, for method 'double_raw': {error}")
            raise error
        finally:
            self.conn.close()
