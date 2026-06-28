import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Set environment variable to force mock ML during tests
os.environ["USE_MOCK_ML"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///./test_pns.db"

from app.main import app
from app.models.database import Base, get_db

# Create engines and session for test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_pns.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    # Clean up JSON files at start
    for file_name in ["history.json", "feedback.json"]:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
            except Exception:
                pass
    # Create the tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the tables after test finishes
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_pns.db"):
        try:
            os.remove("./test_pns.db")
        except PermissionError:
            pass
    # Clean up JSON files at end
    for file_name in ["history.json", "feedback.json"]:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
            except Exception:
                pass

@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
