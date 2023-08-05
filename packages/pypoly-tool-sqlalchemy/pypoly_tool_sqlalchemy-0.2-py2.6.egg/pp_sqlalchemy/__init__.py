import pypoly
from pypoly.component import Component

__version__ = '0.2'

class Main(Component):
    def init(self):
        pypoly.config.add("database", "")
        pypoly.config.add("debug", False)
        pypoly.config.add("hostname", "localhost")
        pypoly.config.add("password", "")
        pypoly.config.add("pool.max_size", 10)
        pypoly.config.add("pool.recycle", 3600)
        pypoly.config.add("pool.size", 5)
        pypoly.config.add("port", 5432)
        pypoly.config.add("type", "postgres")
        pypoly.config.add("user", "postgres")

    def start(self):
        pypoly.tool.register('db_sa', DB())

class DB(object):
    """
    This class handles the gloabl db connection.
    """
    def __init__(self):
        """
        initalize all values
        """

        self._connection_args = dict()
        self._connection_string =""
        self.engine = None
        self.meta = None

        # create a pool
        import sqlalchemy.pool as pool
        import sqlalchemy as sa
        db_type = pypoly.config.get("type")
        db_type = db_type.lower()

        if db_type == "sqlite":
            self._connection_args = dict(
                #database = pypoly.config.get("database")
            )

            self._connection_string = "sqlite:///" + \
                    pypoly.config.get("database").strip()

            # according to the SQLAlchemy docu NullPool is the best choice for
            # SQLite
            self.engine = sa.create_engine(
                self._connection_string,
                connect_args=self._connection_args,
                poolclass=pool.NullPool,
                echo=pypoly.config.get("debug")
            )

            self.meta = sa.MetaData(bind = self.engine)
            self.meta.reflect()

        elif db_type == "mysql":
            # mysql disconnects after 8 hours of idle time
            # pool_recycle controls max age of a connections
            # See: http://www.sqlalchemy.org/docs/dialects/mysql.html
            self._connection_args = dict(
                host=pypoly.config.get("hostname"),
                port=pypoly.config.get("port"),
                database=pypoly.config.get("database"),
                user=pypoly.config.get("user"),
                password=pypoly.config.get("password")
            )

            self._connection_string = "mysql+mysqldb://"

            self.engine = sa.create_engine(
                self._connection_string,
                connect_args=self._connection_args,
                poolclass=pool.QueuePool,
                max_overflow=pypoly.config.get("pool.max_size"),
                pool_size=pypoly.config.get("pool.size"),
                pool_recycle=pypoly.config.get("pool.recycle"),
                echo=pypoly.config.get("debug")
            )

            self.meta = sa.MetaData(bind = self.engine)
            self.meta.reflect()

        elif db_type == "postgres":
            self._connection_args = dict(
                host=pypoly.config.get("hostname"),
                port=pypoly.config.get("port"),
                database=pypoly.config.get("database"),
                user=pypoly.config.get("user"),
                password=pypoly.config.get("password")
            )

            self._connection_string = "postgres://"

            self.engine = sa.create_engine(
                self._connection_string,
                connect_args=self._connection_args,
                poolclass=pool.QueuePool,
                max_overflow=pypoly.config.get("pool.max_size"),
                pool_size=pypoly.config.get("pool.size"),
                echo=pypoly.config.get("debug")
            )

            self.meta = sa.MetaData(bind = self.engine)
            self.meta.reflect()

        else:
            pypoly.log.error("Unknown DB Type")

    def connect(self):
        return self.engine.connect()
