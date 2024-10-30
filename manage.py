import click
from main import app
from sqlalchemy.orm import sessionmaker
from modules.core.database import Base, engine
from modules.core.services.utils.init_data import init_data

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ATTENTION: Snake case function names are not allowed!


@click.group()
def cli():
    """
    CLI commands for the FastAPI application
    Author: Matheus Henrique (m.araujo)
    Date: 09th September 2024
    """
    pass


@cli.command()
def migrate():
    """
    Create tables (schemas) according to the models, if it doesn't exist on DB
    (It does not update schemas)

    Author: Matheus Henrique (m.araujo)

    Date: 09th September 2024
    """
    # Responsible for create or update DB Schema and stablish connection
    Base.metadata.create_all(bind=engine)
    click.echo("Database tables created.")


@cli.command()
def runserver():
    """
    Run the FastAPI server
    Author: Matheus Henrique (m.araujo)

    Date: 09th September 2024
    """
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)


@cli.command()
def initdata():
    """
    Will generate the initial data (DB) for the sistema first run

    Author: Matheus Henrique (m.araujo)

    Date: 21th October 2024
    """
    init_data()


if __name__ == '__main__':
    cli()
