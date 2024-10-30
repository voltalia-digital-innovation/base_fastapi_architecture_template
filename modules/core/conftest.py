import pytest
from main import app
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from modules.core.database import Base, get_db
from sqlalchemy import create_engine, StaticPool


def pytest_runtest_logstart(nodeid, location):
    """
    The "PASSED" or not cli message when running tests
    The "addopts = -v" of pytest.ini injects the "-v" in the "pytest" command

    Author: Matheus Henrique (m.araujo)

    Date: 20th September 2024
    """
    print(f"Running test: {location[2]}")


# Create a in-memory sqlite DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create the engine with the in-memory DB
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

# Configure the session DB to be available to the tests
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    """
    Create the database schema
    Serve the DB to tests (a new Session per test)
    Kill the DB

    Author: Matheus Henrique (m.araujo)

    Date: 20th September 2024
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    """
    Dependency override
    Will replace the MSSQL DB (default) with the in-memory sqlite to
    attend the tests

    **IMPORTANT**
    This fixture is used once per test.
    It must be a parameter of the test, and imported in the top of the file

    Author: Matheus Henrique (m.araujo)

    Date: 20th September 2024
    """

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
