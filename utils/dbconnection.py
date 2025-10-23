import pymysql
import logging

class DatabaseConnection:

    def __init__(self, host, database, user, password, port=3306):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        self.cursor = None

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                autocommit=False,
                cursorclass=pymysql.cursors.DictCursor
            )

            self.cursor = self.connection.cursor()
            with self.connection.cursor() as temp_cursor:
                temp_cursor.execute("SELECT VERSION()")
                db_version = temp_cursor.fetchone()
                self.logger.info(f"Successfully connected to MySQL Server version {db_version['VERSION()']}")
            return True

        except pymysql.Error as e:
            self.logger.error(f"Error while connecting to MySQL: {e}")
            return False

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            self.logger.info("MySQL connection is closed")

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            result = self.cursor.fetchall()
            return result
        except pymysql.Error as e:
            self.logger.error(f"Error executing query: {e}")
            return None

    def execute_update(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            self.logger.info(f"Query executed successfully. Rows affected: {self.cursor.rowcount}")
            return True
        except pymysql.Error as e:
            self.logger.error(f"Error executing update: {e}")
            self.connection.rollback()
            return False

    def execute_many(self, query, data):
        try:
            self.cursor.executemany(query, data)
            self.connection.commit()
            self.logger.info(f"Batch query executed successfully. Rows affected: {self.cursor.rowcount}")
            return True
        except pymysql.Error as e:
            self.logger.error(f"Error executing batch query: {e}")
            self.connection.rollback()
            return False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()