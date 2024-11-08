from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config.settings import DATABASE_URL

Base = declarative_base()

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # SQLite connection string
        self.engine = create_engine(
            DATABASE_URL, 
            connect_args={"check_same_thread": False}  # Needed for SQLite
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_session(self):
        return self.SessionLocal()

    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine) 