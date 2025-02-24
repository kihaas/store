from alembic import context
from website.models import db
from website import create_app


app = create_app()
app.app_context().push()
target_metadata = db.metadata

def run_migrations_online():
    connectable = db.engine
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()