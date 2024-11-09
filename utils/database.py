from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import DATABASE_URL
import os

# Create Base class for models
Base = declarative_base()

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Get database file path from URL
        db_path = DATABASE_URL.replace('sqlite:///', '')
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
        
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
        
        # Create tables if they don't exist
        if not self.tables_exist():
            self.create_tables()

    def get_session(self):
        return self.SessionLocal()

    def tables_exist(self):
        """Check if all required tables exist in the database"""
        inspector = inspect(self.engine)
        existing_tables = inspector.get_table_names()
        required_tables = ['tasks', 'users']
        return all(table in existing_tables for table in required_tables)

    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)