from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.config import settings

# Determine database URL
SQLALCHEMY_DATABASE_URL = settings.database_url

# Create engine with appropriate settings
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
    
    # Enable foreign key support for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # For PostgreSQL/MySQL and other databases
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)