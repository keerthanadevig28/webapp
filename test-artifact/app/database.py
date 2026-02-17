from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,  
    connect_args={"connect_timeout": 5}  
)

@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Force immediate connection test"""
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("SELECT 1")
    finally:
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates all tables defined in models.
    This is the automatic database bootstrapping required by the assignment.
    """
    import app.models as models  
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")